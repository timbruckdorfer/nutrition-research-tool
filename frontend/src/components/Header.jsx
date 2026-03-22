import { AppBar, Toolbar, Typography, Chip, Box } from '@mui/material'
import { Spa } from '@mui/icons-material'

export default function Header() {
  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        bgcolor: 'transparent',
        borderBottom: '1px solid',
        borderColor: 'grey.200',
      }}
    >
      <Toolbar sx={{ px: { xs: 2, md: 4 } }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            flexGrow: 1,
          }}
        >
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: '10px',
              bgcolor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Spa sx={{ color: 'white', fontSize: 22 }} />
          </Box>
          <Typography
            variant="h6"
            sx={{ color: 'text.primary', fontWeight: 700, fontSize: '1.1rem' }}
          >
            NutriPaper
          </Typography>
        </Box>
        <Chip
          label="GPT-4o"
          size="small"
          sx={{
            bgcolor: 'primary.main',
            color: 'white',
            fontWeight: 600,
            fontSize: '0.7rem',
            height: 26,
          }}
        />
      </Toolbar>
    </AppBar>
  )
}
