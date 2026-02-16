export interface Marker {
  string: number
  fret: number
}

interface GuitarNeckProps {
  stringCount?: number
  tuning?: string
  markers: Marker[]
  onMarkerToggle?: (marker: Marker) => void
  fretCount?: number
  startingFret?: number
}

const FRET_COUNT_DEFAULT = 5

export default function GuitarNeck({
  stringCount = 6,
  tuning = 'EADGBE',
  markers,
  onMarkerToggle,
  fretCount = FRET_COUNT_DEFAULT,
  startingFret = 0,
}: GuitarNeckProps) {
  const tuningLabels = tuning.split('').slice(0, stringCount)

  // Layout constants
  const padding = { top: 40, bottom: 20, left: 50, right: 20 }
  const fretHeight = 60
  const stringSpacing = 44 // 44px minimum for touch targets
  const nutWidth = 6

  const neckWidth = (stringCount - 1) * stringSpacing
  const neckHeight = fretCount * fretHeight

  const svgWidth = padding.left + neckWidth + padding.right
  const svgHeight = padding.top + neckHeight + padding.bottom

  // Compute position helpers
  function stringX(stringIndex: number): number {
    return padding.left + stringIndex * stringSpacing
  }

  function fretY(fretIndex: number): number {
    return padding.top + fretIndex * fretHeight
  }

  // Check if a marker exists at absolute fret position
  function hasMarker(stringIndex: number, absoluteFret: number): boolean {
    return markers.some(
      (m) => m.string === stringIndex && m.fret === absoluteFret,
    )
  }

  // Tap targets emit absolute fret numbers
  function handleTap(stringIndex: number, absoluteFret: number) {
    onMarkerToggle?.({ string: stringIndex, fret: absoluteFret })
  }

  const markerRadius = 14
  const tapTargetSize = 44

  return (
    <svg
      viewBox={`0 0 ${svgWidth} ${svgHeight}`}
      className="w-full max-w-lg"
      role="img"
      aria-label="Guitar neck editor"
    >
      {/* Nut (fret 0) or top fret line */}
      {startingFret === 0 ? (
        <rect
          x={padding.left - nutWidth / 2}
          y={padding.top - nutWidth / 2}
          width={neckWidth + nutWidth}
          height={nutWidth}
          fill="#1f2937"
          rx={1}
        />
      ) : (
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left + neckWidth}
          y2={padding.top}
          stroke="#9ca3af"
          strokeWidth={2}
        />
      )}

      {/* Fret lines */}
      {Array.from({ length: fretCount }, (_, i) => i + 1).map((fret) => (
        <line
          key={`fret-${fret}`}
          x1={padding.left}
          y1={fretY(fret)}
          x2={padding.left + neckWidth}
          y2={fretY(fret)}
          stroke="#9ca3af"
          strokeWidth={2}
        />
      ))}

      {/* Strings */}
      {Array.from({ length: stringCount }, (_, i) => i).map((s) => (
        <line
          key={`string-${s}`}
          x1={stringX(s)}
          y1={padding.top}
          x2={stringX(s)}
          y2={padding.top + neckHeight}
          stroke="#6b7280"
          strokeWidth={s < stringCount / 2 ? 1 : 1.5 + s * 0.2}
        />
      ))}

      {/* String labels (tuning) */}
      {tuningLabels.map((label, i) => (
        <text
          key={`label-${i}`}
          x={stringX(i)}
          y={padding.top - 16}
          textAnchor="middle"
          className="text-xs fill-gray-500"
          fontSize={12}
        >
          {label}
        </text>
      ))}

      {/* Fret numbers */}
      {Array.from({ length: fretCount }, (_, i) => i + 1).map((fret) => (
        <text
          key={`fretnum-${fret}`}
          x={padding.left - 24}
          y={fretY(fret) - fretHeight / 2 + 4}
          textAnchor="middle"
          className="text-xs fill-gray-400"
          fontSize={12}
        >
          {startingFret + fret}
        </text>
      ))}

      {/* Tap targets for fret 0 (nut / open string) - only when startingFret is 0 */}
      {startingFret === 0 &&
        Array.from({ length: stringCount }, (_, s) => (
          <g key={`tap-0-${s}`}>
            <rect
              x={stringX(s) - tapTargetSize / 2}
              y={padding.top - tapTargetSize / 2}
              width={tapTargetSize}
              height={tapTargetSize}
              fill="transparent"
              className="cursor-pointer"
              onClick={() => handleTap(s, 0)}
            />
            {hasMarker(s, 0) && (
              <circle
                cx={stringX(s)}
                cy={padding.top}
                r={markerRadius}
                className="fill-blue-600"
              />
            )}
          </g>
        ))}

      {/* Tap targets and markers for frets 1..fretCount */}
      {Array.from({ length: fretCount }, (_, fretIdx) => fretIdx + 1).map(
        (visualFret) => {
          const absoluteFret = startingFret + visualFret
          return Array.from({ length: stringCount }, (_, s) => {
            const cx = stringX(s)
            const cy = fretY(visualFret) - fretHeight / 2

            return (
              <g key={`tap-${visualFret}-${s}`}>
                <rect
                  x={cx - tapTargetSize / 2}
                  y={cy - tapTargetSize / 2}
                  width={tapTargetSize}
                  height={tapTargetSize}
                  fill="transparent"
                  className="cursor-pointer"
                  onClick={() => handleTap(s, absoluteFret)}
                />
                {hasMarker(s, absoluteFret) && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={markerRadius}
                    className="fill-blue-600"
                  />
                )}
              </g>
            )
          })
        },
      )}
    </svg>
  )
}
