"""
Markov Chain Model for Lick Generation - Phase 7 Week 3

Implements 3rd-order Markov chains for probabilistic lick generation:
- State = previous 2 notes (intervals)
- Predicts next note based on transition probabilities
- Trained on 125-pattern database
- Style-specific models (bebop, gospel, blues, neo-soul, etc.)

Based on research:
- Weimar Jazz Database: 11,000+ pattern instances
- BopLand.org: 1,800+ jazz licks
- 3rd-order provides best quality/speed balance
- Supports rhythm patterns and interval sequences

Features:
- Train models from pattern database
- Generate novel licks using learned probabilities
- Preserve stylistic characteristics
- Length control and termination criteria
"""

from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict, Counter
from dataclasses import dataclass
import random
import pickle
import os


@dataclass
class MarkovState:
    """Markov chain state (2 previous intervals for 3rd-order)"""
    interval1: int  # Previous interval (semitones)
    interval2: int  # Current interval (semitones)

    def __hash__(self):
        return hash((self.interval1, self.interval2))

    def __eq__(self, other):
        return (self.interval1, self.interval2) == (other.interval1, other.interval2)


@dataclass
class MarkovTransition:
    """Transition to next state with probability"""
    next_interval: int
    probability: float
    count: int  # How many times this transition occurred


class MarkovLickModel:
    """3rd-order Markov chain for lick generation"""

    def __init__(self, style: str):
        """
        Initialize Markov model for a specific style

        Args:
            style: Musical style (bebop, gospel, blues, neo_soul, etc.)
        """
        self.style = style

        # Transition tables: state -> list of possible next intervals with probabilities
        self.transitions: Dict[MarkovState, List[MarkovTransition]] = defaultdict(list)

        # Starting states (first 2 intervals of licks)
        self.start_states: List[Tuple[int, int]] = []

        # Ending states (last 2 intervals before resolution)
        self.end_states: Set[MarkovState] = set()

        # Training statistics
        self.total_patterns = 0
        self.total_transitions = 0
        self.trained = False

    def train(self, patterns: List['LickPattern']):
        """
        Train model on lick patterns

        Args:
            patterns: List of LickPattern objects to learn from
        """
        self.total_patterns = len(patterns)

        for pattern in patterns:
            intervals = list(pattern.intervals)

            if len(intervals) < 3:
                continue  # Need at least 3 intervals for 3rd-order

            # Record start state (first 2 intervals)
            self.start_states.append((intervals[0], intervals[1]))

            # Record end state (last 2 intervals)
            end_state = MarkovState(intervals[-2], intervals[-1])
            self.end_states.add(end_state)

            # Build transition table
            for i in range(len(intervals) - 2):
                current_state = MarkovState(intervals[i], intervals[i + 1])
                next_interval = intervals[i + 2]

                # Add transition (will calculate probabilities later)
                self.transitions[current_state].append(
                    MarkovTransition(
                        next_interval=next_interval,
                        probability=0.0,  # Placeholder
                        count=1
                    )
                )

        # Calculate transition probabilities
        self._calculate_probabilities()

        self.trained = True

    def _calculate_probabilities(self):
        """Calculate transition probabilities from counts"""
        for state, transitions in self.transitions.items():
            # Count occurrences of each next interval
            interval_counts = Counter()
            for trans in transitions:
                interval_counts[trans.next_interval] += trans.count

            total_count = sum(interval_counts.values())

            # Calculate probabilities
            self.transitions[state] = [
                MarkovTransition(
                    next_interval=interval,
                    probability=count / total_count,
                    count=count
                )
                for interval, count in interval_counts.items()
            ]

            # Sort by probability (descending)
            self.transitions[state].sort(key=lambda t: t.probability, reverse=True)

            self.total_transitions += len(self.transitions[state])

    def generate(
        self,
        length: int = 8,
        start_interval: Optional[int] = None,
        temperature: float = 1.0,
        prefer_resolution: bool = True
    ) -> List[int]:
        """
        Generate a lick using Markov chain

        Args:
            length: Target length in intervals
            start_interval: Optional starting interval (default: random from training)
            temperature: Randomness control (0=deterministic, 1=normal, >1=more random)
            prefer_resolution: Whether to prefer ending states near the end

        Returns:
            List of intervals (semitones from root)
        """
        if not self.trained:
            raise ValueError("Model not trained. Call train() first.")

        if not self.start_states:
            raise ValueError("No training data available")

        # Initialize with starting state
        if start_interval is not None:
            # Find a start state that begins with this interval
            matching = [s for s in self.start_states if s[0] == start_interval]
            if matching:
                interval1, interval2 = random.choice(matching)
            else:
                interval1, interval2 = random.choice(self.start_states)
        else:
            interval1, interval2 = random.choice(self.start_states)

        generated = [interval1, interval2]

        # Generate remaining intervals
        for i in range(length - 2):
            current_state = MarkovState(generated[-2], generated[-1])

            # Check if we should try to end (near target length and prefer_resolution)
            should_end = prefer_resolution and i >= length - 4 and current_state in self.end_states

            if should_end and random.random() < 0.5:
                break  # End generation

            # Get possible transitions
            transitions = self.transitions.get(current_state, [])

            if not transitions:
                # Dead end - try to find similar state or end
                break

            # Select next interval using weighted random choice with temperature
            next_interval = self._select_transition(transitions, temperature)
            generated.append(next_interval)

        return generated

    def _select_transition(
        self,
        transitions: List[MarkovTransition],
        temperature: float
    ) -> int:
        """
        Select next transition using temperature-controlled sampling

        Args:
            transitions: Available transitions
            temperature: Randomness control

        Returns:
            Selected interval
        """
        if temperature == 0.0:
            # Deterministic: always choose most probable
            return transitions[0].next_interval

        # Apply temperature to probabilities
        probs = [t.probability for t in transitions]

        if temperature != 1.0:
            # Adjust probabilities with temperature
            # Higher temp = more uniform, lower temp = more peaked
            import math
            probs = [math.pow(p, 1.0 / temperature) for p in probs]

            # Renormalize
            total = sum(probs)
            probs = [p / total for p in probs]

        # Weighted random choice
        r = random.random()
        cumulative = 0.0

        for i, prob in enumerate(probs):
            cumulative += prob
            if r <= cumulative:
                return transitions[i].next_interval

        # Fallback to last option
        return transitions[-1].next_interval

    def get_stats(self) -> Dict:
        """Get model statistics"""
        return {
            'style': self.style,
            'trained': self.trained,
            'total_patterns': self.total_patterns,
            'total_states': len(self.transitions),
            'total_transitions': self.total_transitions,
            'start_states': len(self.start_states),
            'end_states': len(self.end_states),
            'avg_transitions_per_state': (
                self.total_transitions / len(self.transitions)
                if self.transitions else 0
            )
        }

    def save(self, filepath: str):
        """Save model to file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'style': self.style,
                'transitions': dict(self.transitions),
                'start_states': self.start_states,
                'end_states': self.end_states,
                'total_patterns': self.total_patterns,
                'total_transitions': self.total_transitions,
                'trained': self.trained
            }, f)

    def load(self, filepath: str):
        """Load model from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.style = data['style']
            self.transitions = defaultdict(list, data['transitions'])
            self.start_states = data['start_states']
            self.end_states = data['end_states']
            self.total_patterns = data['total_patterns']
            self.total_transitions = data['total_transitions']
            self.trained = data['trained']


# ============================================================================
# Model Manager
# ============================================================================

class MarkovModelManager:
    """Manages Markov models for all styles"""

    def __init__(self):
        self.models: Dict[str, MarkovLickModel] = {}
        self.models_dir = "models/markov_licks"

    def train_all_models(self, lick_database: 'LickDatabase'):
        """
        Train Markov models for all styles in database

        Args:
            lick_database: LickDatabase instance with patterns
        """
        print("Training Markov models for all styles...")

        styles = ['bebop', 'gospel', 'blues', 'neo_soul', 'modern_jazz', 'classical']

        for style in styles:
            patterns = lick_database.get_by_style(style)

            if not patterns:
                print(f"  ⚠️  No patterns found for {style}")
                continue

            print(f"\n  Training {style} model ({len(patterns)} patterns)...")
            model = MarkovLickModel(style)
            model.train(patterns)

            self.models[style] = model

            # Print statistics
            stats = model.get_stats()
            print(f"    States: {stats['total_states']}")
            print(f"    Transitions: {stats['total_transitions']}")
            print(f"    Avg transitions/state: {stats['avg_transitions_per_state']:.2f}")

        print(f"\n✅ Trained {len(self.models)} models")

    def get_model(self, style: str) -> Optional[MarkovLickModel]:
        """Get model for a style"""
        return self.models.get(style)

    def generate_lick(
        self,
        style: str,
        length: int = 8,
        temperature: float = 1.0
    ) -> Optional[List[int]]:
        """
        Generate lick using style's Markov model

        Args:
            style: Musical style
            length: Target length
            temperature: Randomness

        Returns:
            List of intervals or None if model not available
        """
        model = self.get_model(style)

        if not model:
            return None

        return model.generate(
            length=length,
            temperature=temperature,
            prefer_resolution=True
        )

    def save_all_models(self):
        """Save all trained models to disk"""
        os.makedirs(self.models_dir, exist_ok=True)

        for style, model in self.models.items():
            filepath = os.path.join(self.models_dir, f"{style}_markov.pkl")
            model.save(filepath)
            print(f"  Saved {style} model to {filepath}")

    def load_all_models(self):
        """Load all saved models from disk"""
        if not os.path.exists(self.models_dir):
            print(f"Models directory not found: {self.models_dir}")
            return

        styles = ['bebop', 'gospel', 'blues', 'neo_soul', 'modern_jazz', 'classical']

        for style in styles:
            filepath = os.path.join(self.models_dir, f"{style}_markov.pkl")

            if os.path.exists(filepath):
                model = MarkovLickModel(style)
                model.load(filepath)
                self.models[style] = model
                print(f"  Loaded {style} model")


# Global model manager instance
markov_model_manager = MarkovModelManager()


# ============================================================================
# Usage Examples and Training Script
# ============================================================================

if __name__ == '__main__':
    from app.pipeline.lick_database_expanded import lick_database

    print("=" * 70)
    print("MARKOV LICK MODEL TRAINING")
    print("=" * 70)

    # Train all models
    markov_model_manager.train_all_models(lick_database)

    # Test generation
    print("\n" + "=" * 70)
    print("SAMPLE GENERATIONS")
    print("=" * 70)

    for style in ['bebop', 'gospel', 'blues', 'neo_soul']:
        model = markov_model_manager.get_model(style)

        if not model:
            continue

        print(f"\n{style.upper()} LICKS:")

        # Generate 3 examples with different temperatures
        for i, temp in enumerate([0.5, 1.0, 1.5], 1):
            intervals = markov_model_manager.generate_lick(
                style=style,
                length=8,
                temperature=temp
            )

            print(f"  {i}. (temp={temp}): {intervals}")

    # Show statistics
    print("\n" + "=" * 70)
    print("MODEL STATISTICS")
    print("=" * 70)

    for style, model in markov_model_manager.models.items():
        stats = model.get_stats()
        print(f"\n{style}:")
        print(f"  Patterns trained: {stats['total_patterns']}")
        print(f"  Unique states: {stats['total_states']}")
        print(f"  Total transitions: {stats['total_transitions']}")
        print(f"  Avg transitions per state: {stats['avg_transitions_per_state']:.2f}")

    # Optionally save models
    print("\n" + "=" * 70)
    print("SAVING MODELS")
    print("=" * 70)

    try:
        markov_model_manager.save_all_models()
        print("✅ All models saved")
    except Exception as e:
        print(f"⚠️  Could not save models: {e}")
