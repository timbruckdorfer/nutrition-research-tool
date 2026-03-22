import { Box, Typography } from '@mui/material'

export default function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        mt: 'auto',
        py: 3,
        textAlign: 'center',
        borderTop: '1px solid',
        borderColor: 'grey.200',
      }}
    >
      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
        Built with React, FastAPI &amp; GPT-4o
      </Typography>
    </Box>
  )
}
