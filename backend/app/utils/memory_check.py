"""System Memory Detection for Safe LLM Model Selection

Detects available system memory and recommends appropriate MLX models
to prevent system crashes from loading models that are too large.

Memory Requirements (approximate for 4-bit quantized models):
- 3B models: ~3-4GB RAM
- 7B models: ~4-6GB RAM
- 8B models: ~5-8GB RAM
- 14B models: ~10-14GB RAM
- 70B models: ~40-50GB RAM (DO NOT load on <64GB systems)
"""

import platform
import subprocess
import logging
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ModelSizeClass(Enum):
    """Model size classifications based on parameter count (ordered by size)"""
    TINY = 1      # <3B params, ~2-3GB RAM
    SMALL = 2     # 3-4B params, ~3-5GB RAM
    MEDIUM = 3    # 7-8B params, ~5-8GB RAM
    LARGE = 4     # 14B params, ~10-14GB RAM
    XLARGE = 5    # 70B+ params, ~40-50GB RAM (dangerous!)


@dataclass
class MemoryInfo:
    """System memory information"""
    total_gb: float
    available_gb: float
    used_gb: float
    
    @property
    def usage_percent(self) -> float:
        return (self.used_gb / self.total_gb) * 100 if self.total_gb > 0 else 0


# Recommended models by memory tier
MEMORY_TIER_MODELS = {
    # 8GB RAM - Use tiny models only
    8: {
        "recommended": "mlx-community/Phi-3.5-mini-instruct-4bit",
        "fallback": None,
        "max_size_class": ModelSizeClass.TINY,
        "warning": "Very limited RAM. Only tiny models (3B) are safe.",
    },
    # 16GB RAM - Small models
    16: {
        "recommended": "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "fallback": "mlx-community/Phi-3.5-mini-instruct-4bit",
        "max_size_class": ModelSizeClass.SMALL,
        "warning": "Limited RAM. Models up to 3-4B are safe.",
    },
    # 24GB RAM - Medium models
    24: {
        "recommended": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "fallback": "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "max_size_class": ModelSizeClass.MEDIUM,
        "warning": "Good RAM. Models up to 7-8B are safe.",
    },
    # 32GB RAM - Medium-Large models
    32: {
        "recommended": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "fallback": "mlx-community/Llama-3.1-8B-Instruct-4bit",
        "max_size_class": ModelSizeClass.MEDIUM,
        "warning": "Good RAM. Models up to 8B are safe. 14B may work with caution.",
    },
    # 48GB RAM - Large models
    48: {
        "recommended": "mlx-community/Qwen2.5-14B-Instruct-4bit",
        "fallback": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "max_size_class": ModelSizeClass.LARGE,
        "warning": "Plenty of RAM. Models up to 14B are safe.",
    },
    # 64GB+ RAM - Can try extra large models (with caution)
    64: {
        "recommended": "mlx-community/Qwen2.5-14B-Instruct-4bit",
        "fallback": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "max_size_class": ModelSizeClass.LARGE,
        "warning": "Excellent RAM. 14B models are safe. 70B models may work but are risky.",
    },
    # 128GB+ RAM - All models safe
    128: {
        "recommended": "mlx-community/Llama-3.3-70B-Instruct-4bit",
        "fallback": "mlx-community/Qwen2.5-14B-Instruct-4bit",
        "max_size_class": ModelSizeClass.XLARGE,
        "warning": "Maximum RAM. All models are safe including 70B.",
    },
}


def get_system_memory() -> MemoryInfo:
    """Get system memory information (macOS-optimized)
    
    Returns:
        MemoryInfo with total, available, and used memory in GB
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return _get_macos_memory()
    elif system == "Linux":
        return _get_linux_memory()
    else:
        # Windows or unknown - return conservative estimate
        logger.warning(f"Unknown system '{system}', using conservative memory estimate")
        return MemoryInfo(total_gb=16.0, available_gb=8.0, used_gb=8.0)


def _get_macos_memory() -> MemoryInfo:
    """Get memory info on macOS using sysctl and vm_stat"""
    try:
        # Get total physical memory
        result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True,
            text=True,
            check=True
        )
        total_bytes = int(result.stdout.strip())
        total_gb = total_bytes / (1024 ** 3)
        
        # Get memory pressure/available using vm_stat
        result = subprocess.run(
            ["vm_stat"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse vm_stat output
        stats = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                # Remove 'Pages' and trailing period, convert to int
                value = value.strip().rstrip('.')
                try:
                    stats[key.strip()] = int(value)
                except ValueError:
                    continue
        
        # Calculate available memory
        page_size = 16384  # macOS typically uses 16KB pages on Apple Silicon
        
        # Try to get page size from vm_stat header
        if 'page size of' in result.stdout:
            try:
                page_size = int(result.stdout.split('page size of')[1].split()[0])
            except (IndexError, ValueError):
                pass
        
        free_pages = stats.get('Pages free', 0)
        inactive_pages = stats.get('Pages inactive', 0)
        speculative_pages = stats.get('Pages speculative', 0)
        
        # Available = free + inactive + speculative (can be reclaimed)
        available_pages = free_pages + inactive_pages + speculative_pages
        available_gb = (available_pages * page_size) / (1024 ** 3)
        
        used_gb = total_gb - available_gb
        
        return MemoryInfo(
            total_gb=round(total_gb, 1),
            available_gb=round(available_gb, 1),
            used_gb=round(used_gb, 1)
        )
        
    except Exception as e:
        logger.error(f"Failed to get macOS memory info: {e}")
        # Return conservative estimate
        return MemoryInfo(total_gb=16.0, available_gb=8.0, used_gb=8.0)


def _get_linux_memory() -> MemoryInfo:
    """Get memory info on Linux using /proc/meminfo"""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = {}
            for line in f:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().split()[0]  # Remove 'kB'
                    meminfo[key] = int(value) * 1024  # Convert to bytes
        
        total_gb = meminfo.get('MemTotal', 0) / (1024 ** 3)
        available_gb = meminfo.get('MemAvailable', meminfo.get('MemFree', 0)) / (1024 ** 3)
        used_gb = total_gb - available_gb
        
        return MemoryInfo(
            total_gb=round(total_gb, 1),
            available_gb=round(available_gb, 1),
            used_gb=round(used_gb, 1)
        )
        
    except Exception as e:
        logger.error(f"Failed to get Linux memory info: {e}")
        return MemoryInfo(total_gb=16.0, available_gb=8.0, used_gb=8.0)


def get_memory_tier(total_gb: float) -> int:
    """Get the appropriate memory tier for the given total RAM
    
    Args:
        total_gb: Total system RAM in GB
        
    Returns:
        Memory tier key (8, 16, 24, 32, 48, 64, or 128)
    """
    tiers = sorted(MEMORY_TIER_MODELS.keys())
    
    for tier in tiers:
        if total_gb < tier * 1.5:  # Allow some headroom
            return tier
    
    return 128  # Maximum tier


def get_recommended_model(
    memory_info: Optional[MemoryInfo] = None,
    prefer_quality: bool = False
) -> Tuple[str, str]:
    """Get the recommended MLX model based on system memory
    
    Args:
        memory_info: Optional pre-fetched memory info
        prefer_quality: If True, prefer larger models within safe limits
        
    Returns:
        Tuple of (recommended_model_path, warning_message)
    """
    if memory_info is None:
        memory_info = get_system_memory()
    
    tier = get_memory_tier(memory_info.total_gb)
    tier_config = MEMORY_TIER_MODELS[tier]
    
    # Log memory detection
    logger.info(f"🔍 System Memory Detection:")
    logger.info(f"   Total: {memory_info.total_gb}GB")
    logger.info(f"   Available: {memory_info.available_gb}GB")
    logger.info(f"   Used: {memory_info.used_gb}GB ({memory_info.usage_percent:.1f}%)")
    logger.info(f"   Memory Tier: {tier}GB")
    logger.info(f"   {tier_config['warning']}")
    
    return tier_config["recommended"], tier_config["warning"]


def is_model_safe(model_path: str, memory_info: Optional[MemoryInfo] = None) -> Tuple[bool, str]:
    """Check if a specific model is safe to load given system memory
    
    Args:
        model_path: HuggingFace model path (e.g., "mlx-community/Llama-3.3-70B-Instruct-4bit")
        memory_info: Optional pre-fetched memory info
        
    Returns:
        Tuple of (is_safe, reason_or_warning)
    """
    if memory_info is None:
        memory_info = get_system_memory()
    
    # Estimate model size from name
    model_lower = model_path.lower()
    
    estimated_ram_gb = 4  # Default for unknown models
    size_class = ModelSizeClass.SMALL
    
    if "70b" in model_lower:
        estimated_ram_gb = 45
        size_class = ModelSizeClass.XLARGE
    elif "14b" in model_lower:
        estimated_ram_gb = 12
        size_class = ModelSizeClass.LARGE
    elif "8b" in model_lower:
        estimated_ram_gb = 6
        size_class = ModelSizeClass.MEDIUM
    elif "7b" in model_lower:
        estimated_ram_gb = 5
        size_class = ModelSizeClass.MEDIUM
    elif "3b" in model_lower or "3.5" in model_lower or "mini" in model_lower:
        estimated_ram_gb = 3
        size_class = ModelSizeClass.SMALL
    elif "1b" in model_lower or "2b" in model_lower:
        estimated_ram_gb = 2
        size_class = ModelSizeClass.TINY
    
    # Check if we have enough available memory (with 10% margin)
    required_with_margin = estimated_ram_gb * 1.1
    
    if memory_info.available_gb < required_with_margin:
        return False, (
            f"❌ UNSAFE: {model_path} requires ~{estimated_ram_gb}GB RAM, "
            f"but only {memory_info.available_gb}GB available. "
            f"This WILL crash your system!"
        )
    
    # Check against memory tier limits
    tier = get_memory_tier(memory_info.total_gb)
    tier_config = MEMORY_TIER_MODELS[tier]
    
    if size_class.value > tier_config["max_size_class"].value:
        return False, (
            f"⚠️ RISKY: {model_path} ({size_class.name} class) exceeds safe limit "
            f"for {memory_info.total_gb}GB RAM system. "
            f"Max safe size: {tier_config['max_size_class'].name}. "
            f"Consider using: {tier_config['recommended']}"
        )
    
    return True, f"✅ SAFE: {model_path} (~{estimated_ram_gb}GB) is within safe limits for your system"


def print_memory_report() -> None:
    """Print a detailed memory report to the console"""
    memory_info = get_system_memory()
    recommended, warning = get_recommended_model(memory_info)
    
    print("\n" + "=" * 60)
    print("🖥️  SYSTEM MEMORY REPORT")
    print("=" * 60)
    print(f"  Total RAM:     {memory_info.total_gb} GB")
    print(f"  Available:     {memory_info.available_gb} GB")
    print(f"  Used:          {memory_info.used_gb} GB ({memory_info.usage_percent:.1f}%)")
    print("-" * 60)
    print(f"  ⚠️  {warning}")
    print("-" * 60)
    print(f"  ✅ Recommended Model: {recommended}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test memory detection
    print_memory_report()
    
    # Test model safety checks
    test_models = [
        "mlx-community/Phi-3.5-mini-instruct-4bit",
        "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "mlx-community/Qwen2.5-14B-Instruct-4bit",
        "mlx-community/Llama-3.3-70B-Instruct-4bit",
    ]
    
    print("\n📋 Model Safety Check:")
    for model in test_models:
        is_safe, message = is_model_safe(model)
        print(f"  {message}")
