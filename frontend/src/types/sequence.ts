export interface SequenceBeat {
  beat_position: number
  chord_id: string | null
}

export interface SequenceMeasure {
  id: string
  position: number
  repeat_start: boolean
  repeat_end: boolean
  ending_number: number | null
  beats: SequenceBeat[]
}

// API response types (from backend)
export interface SequenceBeatApiResponse {
  id: string
  measure_id: string
  beat_position: number
  chord_id: string | null
}

export interface SequenceMeasureApiResponse {
  id: string
  sequence_id: string
  position: number
  repeat_start: boolean
  repeat_end: boolean
  ending_number: number | null
  beats: SequenceBeatApiResponse[]
}

export interface SequenceApiResponse {
  id: string
  song_id: string
  time_signature_numerator: number
  time_signature_denominator: number
  measures_per_line: number
  created_at: string
  updated_at: string
  measures: SequenceMeasureApiResponse[]
}

function buildDefaultBeats(numerator: number): SequenceBeat[] {
  return Array.from({ length: numerator }, (_, i) => ({
    beat_position: i + 1,
    chord_id: null,
  }))
}

export function buildDefaultMeasures(
  count: number,
  numerator: number,
): SequenceMeasure[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `measure-${i}`,
    position: i,
    repeat_start: false,
    repeat_end: false,
    ending_number: null,
    beats: buildDefaultBeats(numerator),
  }))
}
