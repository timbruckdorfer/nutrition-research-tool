import { Box, Button, Typography } from '@mui/material'
import { Download, Refresh } from '@mui/icons-material'

export default function DownloadCard({ onDownload, onReset }) {
  return (
    <Box
      sx={{
        p: { xs: 3, md: 4 },
        borderRadius: 4,
        background: 'linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%)',
        border: '1px solid',
        borderColor: 'success.main',
        textAlign: 'center',
      }}
    >
      <Typography variant="h5" sx={{ color: 'primary.dark', mb: 1 }}>
        Analysis Complete
      </Typography>
      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3 }}>
        Your Excel spreadsheet is ready for download
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<Download />}
          onClick={onDownload}
          sx={{
            bgcolor: 'primary.main',
            '&:hover': { bgcolor: 'primary.dark' },
          }}
        >
          Download Excel
        </Button>
        <Button variant="outlined" startIcon={<Refresh />} onClick={onReset}>
          Analyze More
        </Button>
      </Box>
    </Box>
  )
}
