import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { curriculumApi } from '../../lib/api';
import { X, ChevronLeft, ChevronRight, Loader2, Check, Sparkles } from 'lucide-react';
import { useNavigate } from '@tanstack/react-router';

// Types
interface SkillLevels {
  technical_ability: number;
  theory_knowledge: number;
  rhythm_competency: number;
  ear_training: number;
  improvisation: number;
}

interface StyleFamiliarity {
  gospel: number;
  jazz: number;
  blues: number;
  classical: number;
  neo_soul: number;
  contemporary: number;
}

interface WizardData {
  // Step 1: Skills
  skillLevels: SkillLevels;
  styleFamiliarity: StyleFamiliarity;
  // Step 2: Preferences
  primaryGoal: string;
  weeklyPracticeHours: number;
  learningVelocity: string;
  preferredStyle: string;
  interests: string[];
  // Step 3: Details
  title: string;
  durationWeeks: number;
}

const STORAGE_KEY = 'curriculum_wizard_data';

const defaultData: WizardData = {
  skillLevels: {
    technical_ability: 5,
    theory_knowledge: 5,
    rhythm_competency: 5,
    ear_training: 5,
    improvisation: 5,
  },
  styleFamiliarity: {
    gospel: 5,
    jazz: 5,
    blues: 5,
    classical: 5,
    neo_soul: 5,
    contemporary: 5,
  },
  primaryGoal: '',
  weeklyPracticeHours: 5,
  learningVelocity: '',
  preferredStyle: '',
  interests: [],
  title: 'My Personalized Curriculum',
  durationWeeks: 12,
};

const PRIMARY_GOALS = [
  'Build foundational skills',
  'Master specific techniques',
  'Improvisation & creativity',
  'Performance preparation',
  'Music theory mastery',
];

const LEARNING_VELOCITIES = [
  { value: 'relaxed', label: 'Relaxed', description: '3-5 hrs/week' },
  { value: 'moderate', label: 'Moderate', description: '5-10 hrs/week' },
  { value: 'intensive', label: 'Intensive', description: '10+ hrs/week' },
];

const INTERESTS = [
  'Chord voicings',
  'Rhythm patterns',
  'Scale mastery',
  'Ear training',
  'Improvisation',
  'Sight reading',
];

const STYLES = ['gospel', 'jazz', 'blues', 'classical', 'neo_soul', 'contemporary'];

const DURATION_OPTIONS = [4, 8, 12, 16];

interface CurriculumWizardProps {
  onClose: () => void;
}

export function CurriculumWizard({ onClose }: CurriculumWizardProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentStep, setCurrentStep] = useState(1);
  const [data, setData] = useState<WizardData>(() => {
    // Load from localStorage if exists
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : defaultData;
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Auto-save to localStorage
  useEffect(() => {
    const timer = setTimeout(() => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }, 300);
    return () => clearTimeout(timer);
  }, [data]);

  // Submit assessment mutation
  const assessmentMutation = useMutation({
    mutationFn: async () => {
      return curriculumApi.submitAssessment({
        skill_levels: data.skillLevels,
        style_familiarity: data.styleFamiliarity,
        primary_goal: data.primaryGoal,
        interests: data.interests,
        weekly_practice_hours: data.weeklyPracticeHours,
        learning_velocity: data.learningVelocity,
        preferred_style: data.preferredStyle,
      });
    },
  });

  // Generate curriculum mutation
  const generateMutation = useMutation({
    mutationFn: async () => {
      // First submit assessment
      await assessmentMutation.mutateAsync();
      // Then generate curriculum
      return curriculumApi.generateCurriculum({
        title: data.title,
        duration_weeks: data.durationWeeks,
      });
    },
    onSuccess: () => {
      // Clear localStorage
      localStorage.removeItem(STORAGE_KEY);
      // Invalidate curriculum queries
      queryClient.invalidateQueries({ queryKey: ['curriculum'] });
      // Redirect to dashboard
      setTimeout(() => {
        navigate({ to: '/curriculum' });
      }, 1000);
    },
  });

  const updateData = (updates: Partial<WizardData>) => {
    setData((prev) => ({ ...prev, ...updates }));
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (step === 2) {
      if (!data.primaryGoal) newErrors.primaryGoal = 'Please select your primary goal';
      if (data.weeklyPracticeHours < 1) newErrors.weeklyPracticeHours = 'Must be at least 1 hour';
      if (!data.learningVelocity) newErrors.learningVelocity = 'Please select your learning velocity';
      if (!data.preferredStyle) newErrors.preferredStyle = 'Please select your preferred style';
      if (data.interests.length === 0) newErrors.interests = 'Please select at least one interest';
    }

    if (step === 3) {
      if (!data.title.trim()) newErrors.title = 'Please enter a curriculum title';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (currentStep === 4) return; // Already on generation step

    if (!validateStep(currentStep)) return;

    if (currentStep === 3) {
      // Start generation
      setCurrentStep(4);
      generateMutation.mutate();
    } else {
      setCurrentStep((prev) => Math.min(prev + 1, 4));
    }
  };

  const handleBack = () => {
    if (currentStep === 4 && generateMutation.isPending) return; // Don't allow back during generation
    setCurrentStep((prev) => Math.max(prev - 1, 1));
    setErrors({});
  };

  const handleClose = () => {
    if (currentStep === 4 && generateMutation.isPending) {
      if (!window.confirm('Curriculum generation in progress. Are you sure you want to cancel?')) {
        return;
      }
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="bg-gray-900 rounded-2xl max-w-4xl w-full border border-gray-700 shadow-2xl my-8">
        {/* Header */}
        <div className="relative border-b border-gray-700 p-6">
          <button
            onClick={handleClose}
            className="absolute top-6 right-6 text-gray-400 hover:text-white transition"
            aria-label="Close wizard"
          >
            <X className="w-6 h-6" />
          </button>
          <h2 className="text-2xl font-bold text-white mb-2">Create Your Curriculum</h2>
          <p className="text-gray-400">Step {currentStep} of 4</p>

          {/* Progress Bar */}
          <div className="mt-4 flex gap-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`h-2 flex-1 rounded-full transition-colors ${
                  step <= currentStep ? 'bg-purple-500' : 'bg-gray-700'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 min-h-[400px]">
          {currentStep === 1 && <Step1SkillAssessment data={data} updateData={updateData} />}
          {currentStep === 2 && <Step2LearningPreferences data={data} updateData={updateData} errors={errors} />}
          {currentStep === 3 && <Step3CurriculumDetails data={data} updateData={updateData} errors={errors} />}
          {currentStep === 4 && <Step4Generation mutation={generateMutation} />}
        </div>

        {/* Footer */}
        {currentStep < 4 && (
          <div className="border-t border-gray-700 p-6 flex justify-between">
            <button
              onClick={handleBack}
              disabled={currentStep === 1}
              className="px-6 py-3 bg-gray-700 text-white font-medium rounded-lg hover:bg-gray-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <ChevronLeft className="w-4 h-4" />
              Back
            </button>
            <button
              onClick={handleNext}
              className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-500 transition flex items-center gap-2"
            >
              {currentStep === 3 ? (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Curriculum
                </>
              ) : (
                <>
                  Next
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// Step 1: Skill Assessment
function Step1SkillAssessment({
  data,
  updateData,
}: {
  data: WizardData;
  updateData: (updates: Partial<WizardData>) => void;
}) {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-xl font-semibold text-white mb-4">Assess Your Skills</h3>
        <p className="text-gray-400 mb-6">Rate your current skill level (1 = Beginner, 10 = Expert)</p>

        <div className="space-y-4">
          <SkillSlider
            label="Technical Ability"
            value={data.skillLevels.technical_ability}
            onChange={(val) =>
              updateData({ skillLevels: { ...data.skillLevels, technical_ability: val } })
            }
          />
          <SkillSlider
            label="Theory Knowledge"
            value={data.skillLevels.theory_knowledge}
            onChange={(val) =>
              updateData({ skillLevels: { ...data.skillLevels, theory_knowledge: val } })
            }
          />
          <SkillSlider
            label="Rhythm Competency"
            value={data.skillLevels.rhythm_competency}
            onChange={(val) =>
              updateData({ skillLevels: { ...data.skillLevels, rhythm_competency: val } })
            }
          />
          <SkillSlider
            label="Ear Training"
            value={data.skillLevels.ear_training}
            onChange={(val) =>
              updateData({ skillLevels: { ...data.skillLevels, ear_training: val } })
            }
          />
          <SkillSlider
            label="Improvisation"
            value={data.skillLevels.improvisation}
            onChange={(val) =>
              updateData({ skillLevels: { ...data.skillLevels, improvisation: val } })
            }
          />
        </div>
      </div>

      <div>
        <h3 className="text-xl font-semibold text-white mb-4">Style Familiarity</h3>
        <p className="text-gray-400 mb-6">Rate your familiarity with each style (0 = None, 10 = Expert)</p>

        <div className="space-y-4">
          {STYLES.map((style) => (
            <SkillSlider
              key={style}
              label={style.replace('_', '-').charAt(0).toUpperCase() + style.replace('_', '-').slice(1)}
              value={data.styleFamiliarity[style as keyof StyleFamiliarity]}
              onChange={(val) =>
                updateData({
                  styleFamiliarity: { ...data.styleFamiliarity, [style]: val },
                })
              }
              min={0}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// Step 2: Learning Preferences
function Step2LearningPreferences({
  data,
  updateData,
  errors,
}: {
  data: WizardData;
  updateData: (updates: Partial<WizardData>) => void;
  errors: Record<string, string>;
}) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-6">Learning Preferences</h3>

        {/* Primary Goal */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Primary Goal <span className="text-red-500">*</span>
          </label>
          <select
            value={data.primaryGoal}
            onChange={(e) => updateData({ primaryGoal: e.target.value })}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Select your primary goal...</option>
            {PRIMARY_GOALS.map((goal) => (
              <option key={goal} value={goal}>
                {goal}
              </option>
            ))}
          </select>
          {errors.primaryGoal && <p className="text-red-500 text-sm mt-1">{errors.primaryGoal}</p>}
        </div>

        {/* Weekly Practice Hours */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Weekly Practice Hours <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            min={1}
            max={20}
            value={data.weeklyPracticeHours}
            onChange={(e) => updateData({ weeklyPracticeHours: parseInt(e.target.value) || 0 })}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          {errors.weeklyPracticeHours && <p className="text-red-500 text-sm mt-1">{errors.weeklyPracticeHours}</p>}
        </div>

        {/* Learning Velocity */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Learning Velocity <span className="text-red-500">*</span>
          </label>
          <div className="space-y-3">
            {LEARNING_VELOCITIES.map((velocity) => (
              <label
                key={velocity.value}
                className={`block p-4 border rounded-lg cursor-pointer transition ${
                  data.learningVelocity === velocity.value
                    ? 'border-purple-500 bg-purple-500/10'
                    : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                }`}
              >
                <input
                  type="radio"
                  name="learningVelocity"
                  value={velocity.value}
                  checked={data.learningVelocity === velocity.value}
                  onChange={(e) => updateData({ learningVelocity: e.target.value })}
                  className="sr-only"
                />
                <div className="flex justify-between items-center">
                  <span className="text-white font-medium">{velocity.label}</span>
                  <span className="text-gray-400 text-sm">{velocity.description}</span>
                </div>
              </label>
            ))}
          </div>
          {errors.learningVelocity && <p className="text-red-500 text-sm mt-1">{errors.learningVelocity}</p>}
        </div>

        {/* Preferred Style */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Preferred Style <span className="text-red-500">*</span>
          </label>
          <select
            value={data.preferredStyle}
            onChange={(e) => updateData({ preferredStyle: e.target.value })}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Select your preferred style...</option>
            {STYLES.map((style) => (
              <option key={style} value={style}>
                {style.replace('_', '-').charAt(0).toUpperCase() + style.replace('_', '-').slice(1)}
              </option>
            ))}
          </select>
          {errors.preferredStyle && <p className="text-red-500 text-sm mt-1">{errors.preferredStyle}</p>}
        </div>

        {/* Interests */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Areas of Interest <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-2 gap-3">
            {INTERESTS.map((interest) => (
              <label
                key={interest}
                className={`flex items-center p-3 border rounded-lg cursor-pointer transition ${
                  data.interests.includes(interest)
                    ? 'border-purple-500 bg-purple-500/10'
                    : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                }`}
              >
                <input
                  type="checkbox"
                  checked={data.interests.includes(interest)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      updateData({ interests: [...data.interests, interest] });
                    } else {
                      updateData({ interests: data.interests.filter((i) => i !== interest) });
                    }
                  }}
                  className="mr-3"
                />
                <span className="text-white text-sm">{interest}</span>
              </label>
            ))}
          </div>
          {errors.interests && <p className="text-red-500 text-sm mt-1">{errors.interests}</p>}
        </div>
      </div>
    </div>
  );
}

// Step 3: Curriculum Details
function Step3CurriculumDetails({
  data,
  updateData,
  errors,
}: {
  data: WizardData;
  updateData: (updates: Partial<WizardData>) => void;
  errors: Record<string, string>;
}) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-white mb-6">Curriculum Details</h3>

        {/* Title */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Curriculum Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={data.title}
            onChange={(e) => updateData({ title: e.target.value })}
            placeholder="My Personalized Curriculum"
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
        </div>

        {/* Duration */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Duration (weeks)</label>
          <select
            value={data.durationWeeks}
            onChange={(e) => updateData({ durationWeeks: parseInt(e.target.value) })}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {DURATION_OPTIONS.map((weeks) => (
              <option key={weeks} value={weeks}>
                {weeks} weeks
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Review Summary */}
      <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
        <h4 className="text-lg font-semibold text-white mb-4">Review Your Assessment</h4>

        <div className="space-y-4 text-sm">
          <div>
            <p className="text-gray-400 mb-1">Primary Goal</p>
            <p className="text-white">{data.primaryGoal || 'Not set'}</p>
          </div>
          <div>
            <p className="text-gray-400 mb-1">Weekly Practice</p>
            <p className="text-white">{data.weeklyPracticeHours} hours/week ({data.learningVelocity || 'Not set'})</p>
          </div>
          <div>
            <p className="text-gray-400 mb-1">Preferred Style</p>
            <p className="text-white capitalize">{data.preferredStyle.replace('_', ' ') || 'Not set'}</p>
          </div>
          <div>
            <p className="text-gray-400 mb-1">Interests</p>
            <p className="text-white">{data.interests.join(', ') || 'None selected'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Step 4: Generation
function Step4Generation({ mutation }: { mutation: any }) {
  const steps = [
    { label: 'Analyzing your skill profile...', completed: true },
    { label: 'Generating curriculum modules...', completed: mutation.isSuccess },
    { label: 'Creating practice exercises...', completed: mutation.isSuccess },
    { label: 'Preparing lesson tutorials...', completed: mutation.isSuccess },
  ];

  return (
    <div className="flex flex-col items-center justify-center py-12">
      {mutation.isPending && (
        <>
          <Loader2 className="w-16 h-16 text-purple-500 animate-spin mb-8" />
          <h3 className="text-2xl font-semibold text-white mb-4">Creating Your Curriculum</h3>
          <p className="text-gray-400 mb-8">This may take 30-60 seconds...</p>
        </>
      )}

      {mutation.isSuccess && (
        <>
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mb-8">
            <Check className="w-8 h-8 text-green-500" />
          </div>
          <h3 className="text-2xl font-semibold text-white mb-4">Curriculum Ready!</h3>
          <p className="text-gray-400 mb-8">Redirecting to your dashboard...</p>
        </>
      )}

      {mutation.isError && (
        <>
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mb-8">
            <X className="w-8 h-8 text-red-500" />
          </div>
          <h3 className="text-2xl font-semibold text-white mb-4">Generation Failed</h3>
          <p className="text-gray-400 mb-8">
            {mutation.error?.message || 'An error occurred while generating your curriculum'}
          </p>
          <button
            onClick={() => mutation.mutate()}
            className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-500 transition"
          >
            Try Again
          </button>
        </>
      )}

      <div className="w-full max-w-md space-y-3 mt-8">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center gap-3">
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center ${
                step.completed
                  ? 'bg-green-500'
                  : mutation.isPending && index === 1
                  ? 'bg-purple-500 animate-pulse'
                  : 'bg-gray-700'
              }`}
            >
              {step.completed && <Check className="w-4 h-4 text-white" />}
            </div>
            <span className={`${step.completed ? 'text-white' : 'text-gray-400'}`}>{step.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Reusable Slider Component
function SkillSlider({
  label,
  value,
  onChange,
  min = 1,
  max = 10,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
}) {
  const getColor = (val: number) => {
    if (val <= 3) return 'text-red-400';
    if (val <= 6) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm font-medium text-gray-300">{label}</label>
        <span className={`text-lg font-bold ${getColor(value)}`}>{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
      />
      <div className="flex justify-between text-xs text-gray-500 mt-1">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}
