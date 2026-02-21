import { useState } from 'react'
import { useDroppable } from '@dnd-kit/core'
import type { SequenceMeasure, SequenceBeat } from '../types/sequence'

export interface ChordStaffProps {
  numerator: number
  denominator: number
  measuresPerLine: number
  measures: SequenceMeasure[]
  chordMap: Record<string, string>
  onRemoveBeat: (measureId: string, beatPosition: number) => void
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
  onRemoveBeat,
}: {
  beat: SequenceBeat
  measureId: string
  chordMap: Record<string, string>
  onRemoveBeat: (measureId: string, beatPosition: number) => void
}) {
  const [showMenu, setShowMenu] = useState(false)
  const { setNodeRef, isOver } = useDroppable({
    id: `beat|${measureId}|${beat.beat_position}`,
    data: { type: 'beat', measureId, beatPosition: beat.beat_position },
  })

  const chordName = beat.chord_id ? (chordMap[beat.chord_id] ?? 'Untitled') : null

  return (
    <div className="relative flex-1">
      {showMenu && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
          <div className="absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 rounded border border-gray-200 bg-white shadow-md">
            <button
              type="button"
              onClick={() => {
                onRemoveBeat(measureId, beat.beat_position)
                setShowMenu(false)
              }}
              className="block w-full whitespace-nowrap px-3 py-1.5 text-left text-xs text-red-600 hover:bg-red-50"
            >
              Remove
            </button>
          </div>
        </>
      )}
      <div
        ref={setNodeRef}
        onClick={() => { if (beat.chord_id) setShowMenu((v) => !v) }}
        className={`flex h-12 w-full items-center justify-center rounded border text-xs transition-colors ${
          isOver
            ? 'border-blue-400 bg-blue-50'
            : beat.chord_id
              ? 'cursor-pointer border-gray-300 bg-white hover:border-gray-400'
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
  onRemoveBeat,
}: {
  measure: SequenceMeasure
  chordMap: Record<string, string>
  onRemoveBeat: (measureId: string, beatPosition: number) => void
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
          <BeatSlot
            key={beat.beat_position}
            beat={beat}
            measureId={measure.id}
            chordMap={chordMap}
            onRemoveBeat={onRemoveBeat}
          />
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
  onRemoveBeat,
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
              <Measure measure={measure} chordMap={chordMap} onRemoveBeat={onRemoveBeat} />
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
