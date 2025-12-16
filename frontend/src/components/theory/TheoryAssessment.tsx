/**
 * Theory Assessment Component
 *
 * Theory knowledge testing with:
 * - Multiple choice questions
 * - Chord identification (audio)
 * - Progression analysis
 * - Interactive exercises
 * - Auto-grading with skill profile updates
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    CheckCircle2,
    XCircle,
    AlertCircle,
    ChevronRight,
    Trophy,
    Volume2,
    RefreshCw
} from 'lucide-react';

interface AssessmentQuestion {
    id: string;
    type: 'multiple_choice' | 'audio_identification' | 'progression_analysis';
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
    audio_url?: string;
}

interface TheoryAssessmentProps {
    topicId: string;
    topicName: string;
    studentLevel: string;
    onComplete?: (score: number, passed: boolean) => void;
}

export function TheoryAssessment({
    topicId,
    topicName,
    studentLevel,
    onComplete
}: TheoryAssessmentProps) {
    const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
    const [showResults, setShowResults] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [score, setScore] = useState(0);

    const PASSING_SCORE = 70; // 70% to pass

    // Fetch assessment questions
    useEffect(() => {
        fetchAssessment();
    }, [topicId]);

    const fetchAssessment = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(
                `/api/v1/theory-curriculum/assessment?topic=${topicId}&level=${studentLevel}`
            );
            const data = await response.json();

            if (data.questions) {
                setQuestions(data.questions);
            }
        } catch (error) {
            console.error('Failed to fetch assessment:', error);
            // Use mock questions
            setQuestions(getMockQuestions());
        } finally {
            setIsLoading(false);
        }
    };

    const getMockQuestions = (): AssessmentQuestion[] => {
        return [
            {
                id: '1',
                type: 'multiple_choice',
                question: 'What is a tritone substitution?',
                options: [
                    'Replacing a chord with another a half step away',
                    'Replacing a dominant 7th chord with another dominant 7th a tritone away',
                    'Replacing a major chord with its relative minor',
                    'Replacing a chord with its parallel major/minor'
                ],
                correct_answer: 'Replacing a dominant 7th chord with another dominant 7th a tritone away',
                explanation: 'A tritone substitution replaces a dominant 7th chord (like G7) with another dominant 7th chord a tritone (3 whole steps) away (like Db7). This works because they share the same tritone interval (3rd and 7th).'
            },
            {
                id: '2',
                type: 'multiple_choice',
                question: 'In Neo-Riemannian theory, what does the "P" transformation do?',
                options: [
                    'Moves to the parallel major/minor (keeps root, changes quality)',
                    'Moves to the relative major/minor',
                    'Moves by leading tone exchange',
                    'Inverts the chord'
                ],
                correct_answer: 'Moves to the parallel major/minor (keeps root, changes quality)',
                explanation: 'The P (Parallel) transformation keeps the root note the same but changes between major and minor. For example, C major → C minor.'
            },
            {
                id: '3',
                type: 'multiple_choice',
                question: 'What is negative harmony based on?',
                options: [
                    'Using only minor chords',
                    'Mirroring chords across an axis in the key',
                    'Inverting chord voicings',
                    'Playing progressions backwards'
                ],
                correct_answer: 'Mirroring chords across an axis in the key',
                explanation: 'Negative harmony creates mirror-image harmonic relationships by reflecting chords across an axis between the tonic and subdominant in a key.'
            },
            {
                id: '4',
                type: 'multiple_choice',
                question: 'What characterizes the Coltrane Changes?',
                options: [
                    'Rapid modulation through three tonal centers a major third apart',
                    'Extended use of altered dominants',
                    'Modal interchange throughout',
                    'Chromatic bass movement'
                ],
                correct_answer: 'Rapid modulation through three tonal centers a major third apart',
                explanation: 'Coltrane Changes (from "Giant Steps") move rapidly through three keys separated by major thirds (e.g., B, Eb, G), with each preceded by its dominant.'
            },
            {
                id: '5',
                type: 'multiple_choice',
                question: 'What is a key principle of good voice leading?',
                options: [
                    'Always move all voices in the same direction',
                    'Minimize voice movement and retain common tones',
                    'Jump large intervals for dramatic effect',
                    'Never use parallel motion'
                ],
                correct_answer: 'Minimize voice movement and retain common tones',
                explanation: 'Good voice leading aims for smooth, efficient movement by minimizing the distance each voice travels and retaining common tones between chords when possible.'
            }
        ];
    };

    const handleSelectAnswer = (optionIndex: number) => {
        const option = questions[currentQuestion].options[optionIndex];
        setSelectedAnswers({
            ...selectedAnswers,
            [currentQuestion]: option
        });
    };

    const handleNext = () => {
        if (currentQuestion < questions.length - 1) {
            setCurrentQuestion(currentQuestion + 1);
        } else {
            // Calculate score and show results
            calculateScore();
        }
    };

    const handlePrevious = () => {
        if (currentQuestion > 0) {
            setCurrentQuestion(currentQuestion - 1);
        }
    };

    const calculateScore = () => {
        let correct = 0;
        questions.forEach((q, index) => {
            if (selectedAnswers[index] === q.correct_answer) {
                correct++;
            }
        });

        const percentage = Math.round((correct / questions.length) * 100);
        setScore(percentage);
        setShowResults(true);

        // Callback
        if (onComplete) {
            onComplete(percentage, percentage >= PASSING_SCORE);
        }
    };

    const handleRetake = () => {
        setSelectedAnswers({});
        setCurrentQuestion(0);
        setShowResults(false);
        setScore(0);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-gray-400">Loading assessment...</div>
            </div>
        );
    }

    if (showResults) {
        const passed = score >= PASSING_SCORE;
        const correctCount = Math.round((score / 100) * questions.length);

        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-gray-800/50 rounded-xl border border-gray-700 p-8"
            >
                {/* Results Header */}
                <div className="text-center mb-8">
                    {passed ? (
                        <Trophy className="w-20 h-20 mx-auto mb-4 text-yellow-500" />
                    ) : (
                        <AlertCircle className="w-20 h-20 mx-auto mb-4 text-orange-500" />
                    )}

                    <h2 className="text-3xl font-bold text-white mb-2">
                        {passed ? 'Congratulations!' : 'Keep Practicing!'}
                    </h2>

                    <div className="text-6xl font-bold text-white mb-4">
                        {score}%
                    </div>

                    <p className="text-gray-400">
                        You got {correctCount} out of {questions.length} questions correct
                    </p>

                    {passed ? (
                        <div className="mt-4 px-6 py-3 bg-green-500/20 border border-green-500/30 rounded-lg inline-block">
                            <p className="text-green-400 font-medium">
                                You've mastered {topicName}!
                            </p>
                        </div>
                    ) : (
                        <div className="mt-4 px-6 py-3 bg-orange-500/20 border border-orange-500/30 rounded-lg inline-block">
                            <p className="text-orange-400 font-medium">
                                You need {PASSING_SCORE}% to pass. Review the material and try again!
                            </p>
                        </div>
                    )}
                </div>

                {/* Question Review */}
                <div className="space-y-4 mb-8">
                    <h3 className="text-white font-semibold mb-4">Review Your Answers</h3>

                    {questions.map((question, index) => {
                        const userAnswer = selectedAnswers[index];
                        const isCorrect = userAnswer === question.correct_answer;

                        return (
                            <div
                                key={question.id}
                                className={`
                                    p-4 rounded-lg border-2
                                    ${isCorrect
                                        ? 'bg-green-500/10 border-green-500/30'
                                        : 'bg-red-500/10 border-red-500/30'
                                    }
                                `}
                            >
                                <div className="flex items-start gap-3">
                                    {isCorrect ? (
                                        <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-1" />
                                    ) : (
                                        <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-1" />
                                    )}

                                    <div className="flex-1">
                                        <p className="text-white font-medium mb-2">
                                            {index + 1}. {question.question}
                                        </p>

                                        {!isCorrect && (
                                            <div className="space-y-1 text-sm">
                                                <p className="text-red-400">
                                                    Your answer: {userAnswer || '(not answered)'}
                                                </p>
                                                <p className="text-green-400">
                                                    Correct answer: {question.correct_answer}
                                                </p>
                                            </div>
                                        )}

                                        <p className="text-gray-400 text-sm mt-2">
                                            {question.explanation}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Actions */}
                <div className="flex gap-4">
                    <button
                        onClick={handleRetake}
                        className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg text-white font-semibold transition-colors"
                    >
                        <RefreshCw className="w-5 h-5" />
                        Retake Assessment
                    </button>

                    {passed && (
                        <button className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-500 rounded-lg text-white font-semibold transition-colors">
                            Continue to Next Topic
                        </button>
                    )}
                </div>
            </motion.div>
        );
    }

    // Assessment in progress
    const question = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;
    const selectedAnswer = selectedAnswers[currentQuestion];

    return (
        <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-8">
            {/* Progress */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">
                        Question {currentQuestion + 1} of {questions.length}
                    </span>
                    <span className="text-sm font-medium text-white">
                        {Math.round(progress)}%
                    </span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                    />
                </div>
            </div>

            {/* Question */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentQuestion}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                >
                    <h3 className="text-2xl font-semibold text-white mb-6">
                        {question.question}
                    </h3>

                    {/* Audio playback (if applicable) */}
                    {question.audio_url && (
                        <button className="mb-6 flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white transition-colors">
                            <Volume2 className="w-5 h-5" />
                            Play Audio Example
                        </button>
                    )}

                    {/* Options */}
                    <div className="space-y-3 mb-8">
                        {question.options.map((option, index) => (
                            <button
                                key={index}
                                onClick={() => handleSelectAnswer(index)}
                                className={`
                                    w-full p-4 rounded-lg border-2 text-left transition-all
                                    ${selectedAnswer === option
                                        ? 'bg-purple-500/20 border-purple-500 text-white'
                                        : 'bg-gray-900/50 border-gray-700 text-gray-300 hover:border-purple-500/50 hover:bg-purple-500/5'
                                    }
                                `}
                            >
                                <div className="flex items-start gap-3">
                                    <span className={`
                                        flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center
                                        ${selectedAnswer === option
                                            ? 'border-purple-500 bg-purple-500'
                                            : 'border-gray-600'
                                        }
                                    `}>
                                        {selectedAnswer === option && (
                                            <div className="w-2 h-2 bg-white rounded-full" />
                                        )}
                                    </span>
                                    <span>{option}</span>
                                </div>
                            </button>
                        ))}
                    </div>

                    {/* Navigation */}
                    <div className="flex items-center justify-between">
                        <button
                            onClick={handlePrevious}
                            disabled={currentQuestion === 0}
                            className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Previous
                        </button>

                        <button
                            onClick={handleNext}
                            disabled={!selectedAnswer}
                            className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {currentQuestion === questions.length - 1 ? 'Submit' : 'Next'}
                            <ChevronRight className="w-5 h-5" />
                        </button>
                    </div>
                </motion.div>
            </AnimatePresence>
        </div>
    );
}
