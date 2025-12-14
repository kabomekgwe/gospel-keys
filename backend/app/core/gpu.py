"""GPU Device Detection and Configuration Utility

Provides automatic GPU detection and selection for MIDI generation tasks.
Supports Apple Silicon MPS, NVIDIA CUDA, and CPU fallback.
"""

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal, Optional

import torch

logger = logging.getLogger(__name__)

DeviceType = Literal["mps", "cuda", "cpu"]


@dataclass
class GPUInfo:
    """GPU device information."""
    device_type: DeviceType
    device_name: str
    available: bool
    memory_total_gb: Optional[float] = None
    memory_available_gb: Optional[float] = None


@lru_cache(maxsize=1)
def get_device() -> torch.device:
    """
    Auto-detect and return the best available device.
    
    Priority: MPS (Apple Silicon) > CUDA (NVIDIA) > CPU
    
    Returns:
        torch.device: Best available device for tensor operations
    """
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        logger.info("Using MPS (Apple Silicon GPU) for acceleration")
        return torch.device("mps")
    
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        logger.info(f"Using CUDA GPU: {device_name}")
        return torch.device("cuda")
    
    logger.info("No GPU available, using CPU")
    return torch.device("cpu")


def is_gpu_available() -> bool:
    """Check if any GPU (MPS or CUDA) is available."""
    return (
        torch.backends.mps.is_available() or 
        torch.cuda.is_available()
    )


def get_device_info() -> GPUInfo:
    """
    Get detailed information about the current device.
    
    Returns:
        GPUInfo: Device information including type, name, and memory stats
    """
    device = get_device()
    device_type = device.type
    
    if device_type == "mps":
        return GPUInfo(
            device_type="mps",
            device_name="Apple Silicon GPU",
            available=True,
            # MPS doesn't expose memory stats directly
            memory_total_gb=None,
            memory_available_gb=None,
        )
    
    if device_type == "cuda":
        props = torch.cuda.get_device_properties(0)
        memory_total = props.total_memory / (1024 ** 3)
        memory_free = torch.cuda.memory_reserved(0) / (1024 ** 3)
        
        return GPUInfo(
            device_type="cuda",
            device_name=props.name,
            available=True,
            memory_total_gb=round(memory_total, 2),
            memory_available_gb=round(memory_total - memory_free, 2),
        )
    
    return GPUInfo(
        device_type="cpu",
        device_name="CPU",
        available=False,
        memory_total_gb=None,
        memory_available_gb=None,
    )


def warmup_device(device: Optional[torch.device] = None) -> None:
    """
    Warm up the GPU to reduce first-inference latency.
    
    Creates a small tensor and performs basic operations to initialize
    the GPU compute pipeline.
    
    Args:
        device: Device to warm up (auto-detected if None)
    """
    if device is None:
        device = get_device()
    
    if device.type == "cpu":
        return
    
    logger.debug(f"Warming up {device.type} device...")
    
    # Create small test tensor and perform basic ops
    try:
        x = torch.randn(100, 100, device=device)
        _ = torch.matmul(x, x)
        
        # Synchronize for CUDA
        if device.type == "cuda":
            torch.cuda.synchronize()
        elif device.type == "mps":
            # MPS sync
            torch.mps.synchronize()
        
        del x
        logger.debug(f"Device {device.type} warmed up successfully")
    except Exception as e:
        logger.warning(f"Device warmup failed: {e}")


def to_device(tensor: torch.Tensor, device: Optional[torch.device] = None) -> torch.Tensor:
    """
    Move tensor to the specified or default device.
    
    Args:
        tensor: Input tensor
        device: Target device (auto-detected if None)
    
    Returns:
        Tensor on the target device
    """
    if device is None:
        device = get_device()
    return tensor.to(device)


def clear_gpu_cache() -> None:
    """Clear GPU memory cache to free unused memory."""
    device = get_device()
    
    if device.type == "cuda":
        torch.cuda.empty_cache()
        logger.debug("CUDA cache cleared")
    elif device.type == "mps":
        # MPS cache clearing (if available in future PyTorch versions)
        try:
            torch.mps.empty_cache()
            logger.debug("MPS cache cleared")
        except AttributeError:
            pass  # Not available in this PyTorch version
