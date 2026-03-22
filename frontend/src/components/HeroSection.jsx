import { Box, Typography } from '@mui/material'
import { AutoAwesome } from '@mui/icons-material'

export default function HeroSection() {
  return (
    <Box
      sx={{
        py: { xs: 5, md: 7 },
        px: 3,
        textAlign: 'center',
        background: 'linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 50%, #FFF8E1 100%)',
        borderBottom: '1px solid',
        borderColor: 'grey.200',
      }}
    >
      <Box
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 1,
          bgcolor: 'white',
          border: '1px solid',
          borderColor: 'grey.200',
          borderRadius: '20px',
          px: 2,
          py: 0.5,
          mb: 3,
        }}
      >
        <AutoAwesome sx={{ fontSize: 16, color: 'secondary.main' }} />
        <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
          AI-Powered Research Analysis
        </Typography>
      </Box>
      <Typography
        variant="h3"
        sx={{
          maxWidth: 700,
          mx: 'auto',
          mb: 2,
          fontSize: { xs: '1.75rem', md: '2.5rem' },
          color: 'text.primary',
        }}
      >
        Extract Structured Data from Nutrition Research Papers
      </Typography>
      <Typography
        variant="body1"
        sx={{
          maxWidth: 560,
          mx: 'auto',
          color: 'text.secondary',
          lineHeight: 1.7,
          fontSize: { xs: '0.95rem', md: '1.05rem' },
        }}
      >
        Upload PDFs and automatically extract authors, methodology, study details,
        and more &mdash; exported to a clean Excel spreadsheet.
      </Typography>
    </Box>
  )
}
