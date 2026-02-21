import { useDroppable } from '@dnd-kit/core'
import type { SequenceMeasure, SequenceBeat } from '../types/sequence'

export interface ChordStaffProps {
  numerator: number
  denominator: number
  measuresPerLine: number
  measures: SequenceMeasure[]
  chordMap: Record<string, string>
}

function TimeSignature({ numerator, denominator }: { numerator: number; denominator: number }) {
  return (
    <div className="flex flex-col items-center justify-center px-2 text-center leading-none">
      <span className="text-xl font-bold text-gray-700">{numerator}</span>
      <span className="text-xl font-bold text-gray-700">{denominator}</span>
    </div>
  )
}

function BeatSlot({
  beat,
  measureId,
  chordMap,
}: {
  beat: SequenceBeat
  measureId: string
  chordMap: Record<string, string>
}) {
  const { setNodeRef, isOver } = useDroppable({
    id: `beat|${measureId}|${beat.beat_position}`,
    data: { type: 'beat', measureId, beatPosition: beat.beat_position },
  })

  const chordName = beat.chord_id ? (chordMap[beat.chord_id] ?? 'Untitled') : null

  return (
    <div
      ref={setNodeRef}
      className={`flex h-12 w-full items-center justify-center rounded border text-xs transition-colors ${
        isOver
          ? 'border-blue-400 bg-blue-50'
          : beat.chord_id
            ? 'border-gray-300 bg-white'
            : 'border-dashed border-gray-300 bg-white text-gray-400'
      }`}
      aria-label={`Beat ${beat.beat_position}`}
    >
      {chordName === null ? (
        <span className="select-none opacity-50">—</span>
      ) : (
        <span className="font-medium text-gray-800">{chordName}</span>
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

function Measure({
  measure,
  chordMap,
}: {
  measure: SequenceMeasure
  chordMap: Record<string, string>
}) {
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
          <BeatSlot key={beat.beat_position} beat={beat} measureId={measure.id} chordMap={chordMap} />
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
  chordMap,
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
              <Measure measure={measure} chordMap={chordMap} />
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
