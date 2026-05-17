/**
 * RiskMeter — Animated circular gauge showing overall risk score.
 * Displays score 0-100 with color gradient from green to red.
 */

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

const GRADE_COLORS = {
  A: '#2ec4b6',
  B: '#4cc9f0',
  C: '#f7b32b',
  D: '#ff6b35',
  F: '#ef233c',
}

export default function RiskMeter({ score = 0, grade = 'N/A', size = 240 }) {
  const [animatedScore, setAnimatedScore] = useState(0)

  useEffect(() => {
    // Animate score counting up
    const duration = 1500
    const steps = 60
    const increment = score / steps
    let current = 0
    const interval = setInterval(() => {
      current += increment
      if (current >= score) {
        setAnimatedScore(score)
        clearInterval(interval)
      } else {
        setAnimatedScore(Math.round(current))
      }
    }, duration / steps)

    return () => clearInterval(interval)
  }, [score])

  const center = size / 2
  const radius = (size - 24) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference * 0.75 // 270° arc
  const gradeColor = GRADE_COLORS[grade] || '#6c757d'

  // Calculate color based on score
  const getScoreColor = (s) => {
    if (s <= 15) return '#2ec4b6'
    if (s <= 30) return '#4cc9f0'
    if (s <= 50) return '#f7b32b'
    if (s <= 70) return '#ff6b35'
    return '#ef233c'
  }

  const scoreColor = getScoreColor(animatedScore)

  return (
    <motion.div
      className="score-gauge-wrapper"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={scoreColor} />
            <stop offset="100%" stopColor={gradeColor} />
          </linearGradient>
        </defs>

        {/* Background arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth="8"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeLinecap="round"
          transform={`rotate(135 ${center} ${center})`}
        />

        {/* Score arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="url(#scoreGradient)"
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(135 ${center} ${center})`}
          filter="url(#glow)"
          style={{ transition: 'stroke-dashoffset 1.5s ease-out' }}
        />

        {/* Score text */}
        <text
          x={center}
          y={center - 12}
          textAnchor="middle"
          fill={scoreColor}
          fontSize="48"
          fontWeight="800"
          fontFamily="Inter, sans-serif"
        >
          {animatedScore}
        </text>

        {/* Score label */}
        <text
          x={center}
          y={center + 16}
          textAnchor="middle"
          fill="rgba(255,255,255,0.4)"
          fontSize="12"
          fontWeight="500"
          fontFamily="Inter, sans-serif"
          textTransform="uppercase"
          letterSpacing="0.15em"
        >
          RISK SCORE
        </text>

        {/* Grade */}
        <text
          x={center}
          y={center + 44}
          textAnchor="middle"
          fill={gradeColor}
          fontSize="24"
          fontWeight="800"
          fontFamily="Inter, sans-serif"
        >
          Grade: {grade}
        </text>
      </svg>
    </motion.div>
  )
}
