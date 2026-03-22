import { Box, Button, Chip, LinearProgress, Typography } from '@mui/material'
import { Science, CheckCircle } from '@mui/icons-material'

export default function AnalyzeSection({
  uploadedCount,
  analyzing,
  excelId,
  progress,
  onAnalyze,
}) {
  const showProgress = progress > 0 && progress < 100

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<Science />}
          onClick={onAnalyze}
          disabled={uploadedCount === 0 || analyzing || !!excelId}
          sx={{
            bgcolor: 'primary.main',
            '&:hover': { bgcolor: 'primary.dark' },
          }}
        >
          {analyzing ? 'Analyzing...' : 'Analyze Papers'}
        </Button>

        {uploadedCount > 0 && !excelId && (
          <Chip
            icon={<CheckCircle />}
            label={`${uploadedCount} file${uploadedCount > 1 ? 's' : ''} ready`}
            color="success"
            variant="outlined"
            size="small"
          />
        )}
      </Box>

      {showProgress && (
        <Box sx={{ mt: 3 }}>
          <LinearProgress variant="determinate" value={progress} />
          <Typography
            variant="caption"
            sx={{ mt: 1, display: 'block', color: 'text.secondary' }}
          >
            {progress < 40
              ? 'Uploading files...'
              : progress < 90
                ? `Analyzing ${uploadedCount} paper${uploadedCount > 1 ? 's' : ''} with AI (est. ${Math.ceil(uploadedCount * 1.5)} min)...`
                : 'Generating Excel file...'}
          </Typography>
        </Box>
      )}
    </Box>
  )
}
