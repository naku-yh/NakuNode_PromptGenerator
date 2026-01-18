import torch
import comfy
from comfy.model_patcher import ModelPatcher
from functools import partial
from torch import nn
from typing import Optional
from types import MethodType
from einops import repeat
from comfy.ldm.modules.attention import CrossAttention, default, optimized_attention, optimized_attention_masked
from comfy.ldm.modules.diffusionmodules.mmdit import OpenAISignatureMMDITWrapper, JointBlock

def nag(out_cond, out_nag, nag_scale, nag_tau, nag_alpha):
    """
    NAG算法核心实现
    out_cond: 条件输出
    out_nag: nag负条件输出
    """
    out_guidance = out_cond * nag_scale - out_nag * (nag_scale - 1)
    norm_positive = torch.norm(out_cond, p=1, dim=-1, keepdim=True)
    norm_guidance = torch.norm(out_guidance, p=1, dim=-1, keepdim=True)
    scale = (norm_guidance / norm_positive).clamp_max(nag_tau)
    out_guidance = out_guidance * scale
    return out_guidance * nag_alpha + out_cond * (1 - nag_alpha)

class AIO_NAG:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("MODEL",), 
            "nag_negative": ("CONDITIONING",),
            "nag_scale": ("FLOAT", {"default": 5.0, "min": 1.0, "max": 100.0, "step": 0.1}),
            "nag_tau": ("FLOAT", {"default": 2.5, "min": 1.0, "max": 10.0, "step": 0.1}),
            "nag_alpha": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 1.0, "step": 0.01})
        }}
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "apply_nag"
    CATEGORY = "Model"

    def apply_nag(self, model, nag_negative, nag_scale, nag_tau, nag_alpha):
        # 实现 NAG (Normalized Attention Guidance) 算法
        def nag_patched_call(model_object, x, timestep, cond, uncond, **kwargs):
            # 获取 nag_negative 的条件数据
            nag_cond_data = nag_negative[0][0]  # nag_negative 是 conditioning，格式是 [(cond_data, ...), ...]

            # 构建批次: [uncond, cond, nag_negative] - 用于三元批次处理
            batched_cond = torch.cat([uncond, cond, nag_cond_data], dim=0)

            # 调用原始模型函数
            model_output = model_object.inner_model(x, timestep, cond=batched_cond, **kwargs)

            # 分离输出
            batch_size = uncond.shape[0]
            out_uncond = model_output[:batch_size]
            out_cond = model_output[batch_size:batch_size*2]
            out_nag = model_output[batch_size*2:]

            # 应用 NAG 算法
            out_guided = nag(out_cond, out_nag, nag_scale, nag_tau, nag_alpha)

            # 应用CFG (Classifier-Free Guidance)
            # 从kwargs中获取cond_scale，如果没有则默认为7.0
            cond_scale = kwargs.get('cond_scale', 7.0)
            return out_uncond + cond_scale * (out_guided - out_uncond)

        # 克隆模型
        m = model.clone()
        
        # 保存原始前向函数
        if not hasattr(m.model, 'nag_original_forward'):
            m.model.nag_original_forward = m.model.__call__
        
        # 定义补丁函数
        def nag_patched_forward(x, timestep, cond, uncond, **kwargs):
            return nag_patched_call(m.model, x, timestep, cond, uncond, **kwargs)
        
        # 应用补丁
        m.model.__call__ = nag_patched_forward
        return (m,)


# =================================================================================
# SECTION 2: NOISE ADDED GUIDANCE (Original Nunchaku method)
# =================================================================================

class NoiseAddedGuider:
    def __init__(self, model, nag_strength, nag_start_step, noise_type, seed):
        self.model, self.nag_strength, self.nag_start_step, self.noise_type, self.seed = model, nag_strength, nag_start_step, noise_type, seed
        if hasattr(self.model, "model_sampling"): self.model_sampling = self.model.model_sampling
        elif hasattr(self.model, "model") and hasattr(self.model.model, "model_sampling"): self.model_sampling = self.model.model.model_sampling
        else: raise AttributeError("Cannot find 'model_sampling' component.")
    def __call__(self, x, sigma, uncond, cond, cond_scale, **kwargs):
        cond_pred = self.model(x, sigma, cond=cond, **kwargs)
        uncond_pred = self.model(x, sigma, cond=uncond, **kwargs)
        guided_pred = uncond_pred + (cond_pred - uncond_pred) * cond_scale
        current_step = kwargs.get('total_steps', 1000) - kwargs.get('i', 999) - 1
        if self.nag_strength > 0 and current_step >= self.nag_start_step:
            noise_sampler = self.get_noise_sampler(self.noise_type, self.seed, x.device)
            nag_noise = noise_sampler(guided_pred, None) * self.nag_strength
            noise_pred = self.model_sampling.noise_from_pred(guided_pred, sigma)
            return self.model_sampling.pred_from_noise(noise_pred + nag_noise, sigma)
        return guided_pred
    def __getattr__(self, name):
        try: return getattr(self.model, name)
        except AttributeError: raise AttributeError(f"'{type(self).__name__}' object and its wrapped model have no attribute '{name}'")
    def copy(self): return NoiseAddedGuider(self.model, self.nag_strength, self.nag_start_step, self.noise_type, self.seed)
    def get_noise_sampler(self, noise_type, seed, device):
        if noise_type == 'gaussian':
            def noise_sampler_func(sigma, sigma_next):
                torch.manual_seed(seed)
                return torch.randn_like(sigma, device=device)
            return noise_sampler_func
        elif noise_type == 'uniform':
            def noise_sampler_func(sigma, sigma_next):
                torch.manual_seed(seed)
                return torch.empty_like(sigma, device=device).uniform_(-1, 1)
            return noise_sampler_func
        raise ValueError(f"Unknown noise type: {noise_type}")

class NakuNodeNoiseGuider:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"model": ("MODEL",), "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}), "noise_type": (["gaussian", "uniform"],), "nag_strength": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 10.0, "step": 0.01}), "nag_start_step": ("INT", {"default": 0, "min": 0, "max": 10000})}}
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "guide"
    CATEGORY = "Model"
    def guide(self, model, seed, noise_type, nag_strength, nag_start_step):
        noise_guider = NoiseAddedGuider(model.model, nag_strength, nag_start_step, noise_type, seed)
        model_clone = model.clone()
        model_clone.model = noise_guider
        return (model_clone,)

# =================================================================================
# SECTION 3: NODE MAPPINGS
# =================================================================================

NODE_CLASS_MAPPINGS = {
    "AIO_NAG": AIO_NAG,
    "NakuNodeNoiseGuider": NakuNodeNoiseGuider,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "AIO_NAG": "NakuNode-AIO-NAG",
    "NakuNodeNoiseGuider": "NakuNode Noise Guider (Original Nunchaku)",
}