import type { SequenceMeasure, SequenceBeat } from '../types/sequence'

export interface ChordStaffProps {
  numerator: number
  denominator: number
  measuresPerLine: number
  measures: SequenceMeasure[]
}

function TimeSignature({ numerator, denominator }: { numerator: number; denominator: number }) {
  return (
    <div className="flex flex-col items-center justify-center px-2 text-center leading-none">
      <span className="text-xl font-bold text-gray-700">{numerator}</span>
      <span className="text-xl font-bold text-gray-700">{denominator}</span>
    </div>
  )
}

function BeatSlot({ beat }: { beat: SequenceBeat }) {
  return (
    <div
      className="flex h-12 w-full items-center justify-center rounded border border-dashed border-gray-300 bg-white text-xs text-gray-400"
      aria-label={`Beat ${beat.beat_position}`}
    >
      {beat.chord_id === null ? (
        <span className="select-none opacity-50">—</span>
      ) : (
        <span className="font-medium text-gray-800">{beat.chord_id}</span>
      )}
    </div>
  )
}

function Barline({ bold = false }: { bold?: boolean }) {
  return (
    <div
      className={`self-stretch ${bold ? 'w-1 bg-gray-700' : 'w-px bg-gray-400'}`}
    />
  )
}

function Measure({ measure }: { measure: SequenceMeasure }) {
  return (
    <div className="flex min-w-0 flex-1 flex-col gap-1 px-1">
      {/* Ending number bracket */}
      {measure.ending_number !== null && (
        <div className="border-l border-t border-gray-500 px-1 text-xs font-medium text-gray-600">
          {measure.ending_number}.
        </div>
      )}
      {/* Beat slots */}
      <div className="flex gap-1">
        {measure.beats.map((beat) => (
          <BeatSlot key={beat.beat_position} beat={beat} />
        ))}
      </div>
    </div>
  )
}

export default function ChordStaff({
  numerator,
  denominator,
  measuresPerLine,
  measures,
}: ChordStaffProps) {
  // Split measures into lines
  const lines: SequenceMeasure[][] = []
  for (let i = 0; i < measures.length; i += measuresPerLine) {
    lines.push(measures.slice(i, i + measuresPerLine))
  }

  return (
    <div className="space-y-3">
      {lines.map((lineMeasures, lineIndex) => (
        <div
          key={lineIndex}
          className="flex items-stretch overflow-x-auto rounded-md border border-gray-200 bg-gray-50 p-2"
        >
          {/* Time signature — only on first line */}
          {lineIndex === 0 && (
            <TimeSignature numerator={numerator} denominator={denominator} />
          )}

          {/* Opening barline */}
          <Barline />

          {lineMeasures.map((measure, measureIndex) => (
            <div key={measure.id} className="flex min-w-0 flex-1 items-stretch">
              <Measure measure={measure} />
              {/* Barline after each measure */}
              {measure.repeat_end ? (
                <>
                  <Barline />
                  <Barline bold />
                </>
              ) : measureIndex === lineMeasures.length - 1 ? (
                // Double barline at end of line
                <>
                  <Barline />
                  <Barline />
                </>
              ) : (
                <Barline />
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
