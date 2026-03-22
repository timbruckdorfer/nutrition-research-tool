import { Box, Typography, Chip } from '@mui/material'

const FIELDS = [
  'Authors',
  'Publication Year',
  'Journal',
  'DOI',
  'Country of Publication',
  'Title',
  'Paper Type',
  'Study Objective',
  'Methodology',
  'Sample Size',
  'Study Duration',
  'Inclusion Criteria',
  'Country of Population',
  'Conclusion',
]

export default function ExtractedFields() {
  return (
    <Box>
      <Typography
        variant="subtitle2"
        sx={{ color: 'text.secondary', mb: 1.5, textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.7rem' }}
      >
        Data Points Extracted
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
        {FIELDS.map((field) => (
          <Chip
            key={field}
            label={field}
            size="small"
            variant="outlined"
            sx={{
              borderColor: 'grey.200',
              color: 'text.secondary',
              fontSize: '0.75rem',
              height: 28,
            }}
          />
        ))}
      </Box>
    </Box>
  )
}
