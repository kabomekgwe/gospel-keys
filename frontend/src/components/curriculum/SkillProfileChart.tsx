import { useMemo } from 'react';
import { TrendingUp } from 'lucide-react';

interface SkillProfileChartProps {
  initialSkills: {
    technical_ability: number;
    theory_knowledge: number;
    rhythm_competency: number;
    ear_training: number;
    improvisation: number;
  };
  currentSkills: {
    technical_ability: number;
    theory_knowledge: number;
    rhythm_competency: number;
    ear_training: number;
    improvisation: number;
  };
}

interface SkillData {
  label: string;
  initial: number;
  current: number;
  growth: number;
}

export function SkillProfileChart({ initialSkills, currentSkills }: SkillProfileChartProps) {
  const skills = useMemo<SkillData[]>(() => {
    return [
      {
        label: 'Technical',
        initial: initialSkills.technical_ability,
        current: currentSkills.technical_ability,
        growth: currentSkills.technical_ability - initialSkills.technical_ability,
      },
      {
        label: 'Theory',
        initial: initialSkills.theory_knowledge,
        current: currentSkills.theory_knowledge,
        growth: currentSkills.theory_knowledge - initialSkills.theory_knowledge,
      },
      {
        label: 'Rhythm',
        initial: initialSkills.rhythm_competency,
        current: currentSkills.rhythm_competency,
        growth: currentSkills.rhythm_competency - initialSkills.rhythm_competency,
      },
      {
        label: 'Ear',
        initial: initialSkills.ear_training,
        current: currentSkills.ear_training,
        growth: currentSkills.ear_training - initialSkills.ear_training,
      },
      {
        label: 'Improv',
        initial: initialSkills.improvisation,
        current: currentSkills.improvisation,
        growth: currentSkills.improvisation - initialSkills.improvisation,
      },
    ];
  }, [initialSkills, currentSkills]);

  const totalGrowth = skills.reduce((sum, skill) => sum + skill.growth, 0);
  const avgGrowth = totalGrowth / skills.length;

  // Radar chart calculations
  const center = 150;
  const maxRadius = 120;
  const angleStep = (2 * Math.PI) / 5;

  const polarToCartesian = (radius: number, angle: number) => {
    const x = center + radius * Math.cos(angle - Math.PI / 2);
    const y = center + radius * Math.sin(angle - Math.PI / 2);
    return { x, y };
  };

  const createPolygonPoints = (values: number[]) => {
    return values
      .map((value, index) => {
        const radius = (value / 10) * maxRadius;
        const angle = index * angleStep;
        const { x, y } = polarToCartesian(radius, angle);
        return `${x},${y}`;
      })
      .join(' ');
  };

  const initialPoints = createPolygonPoints(skills.map((s) => s.initial));
  const currentPoints = createPolygonPoints(skills.map((s) => s.current));

  return (
    <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-white">Skill Profile</h3>
        {avgGrowth > 0 && (
          <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-lg">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">
              +{avgGrowth.toFixed(1)} avg growth
            </span>
          </div>
        )}
      </div>

      <div className="flex flex-col md:flex-row gap-8 items-center">
        {/* Radar Chart */}
        <div className="flex-shrink-0">
          <svg width="300" height="300" viewBox="0 0 300 300" className="overflow-visible">
            {/* Grid circles */}
            {[2, 4, 6, 8, 10].map((level) => (
              <circle
                key={level}
                cx={center}
                cy={center}
                r={(level / 10) * maxRadius}
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
                className="text-gray-700"
                opacity={0.3}
              />
            ))}

            {/* Grid lines */}
            {skills.map((_, index) => {
              const angle = index * angleStep;
              const { x, y } = polarToCartesian(maxRadius, angle);
              return (
                <line
                  key={index}
                  x1={center}
                  y1={center}
                  x2={x}
                  y2={y}
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-gray-700"
                  opacity={0.3}
                />
              );
            })}

            {/* Initial skill polygon */}
            <polygon
              points={initialPoints}
              fill="rgb(147, 51, 234)"
              fillOpacity={0.1}
              stroke="rgb(147, 51, 234)"
              strokeWidth="2"
              strokeOpacity={0.5}
            />

            {/* Current skill polygon */}
            <polygon
              points={currentPoints}
              fill="rgb(139, 92, 246)"
              fillOpacity={0.2}
              stroke="rgb(139, 92, 246)"
              strokeWidth="3"
            />

            {/* Current skill dots */}
            {skills.map((skill, index) => {
              const radius = (skill.current / 10) * maxRadius;
              const angle = index * angleStep;
              const { x, y } = polarToCartesian(radius, angle);
              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="4"
                  fill="rgb(139, 92, 246)"
                  className="drop-shadow-lg"
                />
              );
            })}

            {/* Labels */}
            {skills.map((skill, index) => {
              const angle = index * angleStep;
              const labelRadius = maxRadius + 30;
              const { x, y } = polarToCartesian(labelRadius, angle);
              return (
                <text
                  key={index}
                  x={x}
                  y={y}
                  textAnchor="middle"
                  alignmentBaseline="middle"
                  className="text-sm font-medium fill-gray-300"
                >
                  {skill.label}
                </text>
              );
            })}
          </svg>
        </div>

        {/* Skill Details */}
        <div className="flex-1 w-full">
          <div className="space-y-4">
            {skills.map((skill, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-300">{skill.label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">{skill.initial}/10</span>
                    <span className="text-xs text-gray-400">→</span>
                    <span className="text-sm font-semibold text-white">{skill.current}/10</span>
                    {skill.growth > 0 && (
                      <span className="text-xs text-green-400 font-medium">
                        +{skill.growth.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>

                {/* Progress bar */}
                <div className="relative w-full bg-gray-700 rounded-full h-2">
                  {/* Initial level (background) */}
                  <div
                    className="absolute left-0 top-0 h-2 bg-purple-900/50 rounded-full"
                    style={{ width: `${(skill.initial / 10) * 100}%` }}
                  />
                  {/* Current level */}
                  <div
                    className="absolute left-0 top-0 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
                    style={{ width: `${(skill.current / 10) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="mt-6 pt-4 border-t border-gray-700 flex gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-900/50 rounded-sm" />
              <span className="text-gray-400">Initial</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-500 rounded-sm" />
              <span className="text-gray-400">Current</span>
            </div>
          </div>
        </div>
      </div>

      {/* Growth Summary */}
      {totalGrowth > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-700">
          <h4 className="text-sm font-semibold text-white mb-3">Growth Highlights</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {skills
              .filter((s) => s.growth > 0)
              .sort((a, b) => b.growth - a.growth)
              .slice(0, 3)
              .map((skill, index) => (
                <div key={index} className="flex items-center gap-2 p-2 bg-green-500/10 rounded-lg">
                  <TrendingUp className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-xs text-gray-400 truncate">{skill.label}</p>
                    <p className="text-sm font-semibold text-green-400">
                      +{skill.growth.toFixed(1)} points
                    </p>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
