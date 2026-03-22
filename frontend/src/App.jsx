import { useState, useCallback } from 'react'
import {
  Container,
  Box,
  Alert,
  ThemeProvider,
  CssBaseline,
  Card,
  CardContent,
  Typography,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material'
import axios from 'axios'
import theme from './theme'
import Header from './components/Header'
import HeroSection from './components/HeroSection'
import UploadZone from './components/UploadZone'
import AnalyzeSection from './components/AnalyzeSection'
import DownloadCard from './components/DownloadCard'
import ExtractedFields from './components/ExtractedFields'
import Footer from './components/Footer'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').trim()

const STEPS = ['Upload PDFs', 'Analyze with AI', 'Download Results']

function App() {
  const [files, setFiles] = useState([])
  const [uploadedFileIds, setUploadedFileIds] = useState([])
  const [analyzing, setAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [excelId, setExcelId] = useState(null)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const activeStep = excelId ? 2 : uploadedFileIds.length > 0 ? 1 : 0

  const handleFilesSelected = useCallback((newFiles) => {
    setFiles((prev) => [...prev, ...newFiles])
    setError(null)
    setSuccess(null)
    setExcelId(null)
  }, [])

  const handleRemoveFile = useCallback((index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select at least one PDF file')
      return
    }

    setError(null)
    setProgress(10)

    try {
      const formData = new FormData()
      files.forEach((file) => formData.append('files', file))

      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      setUploadedFileIds(response.data.files.map((f) => f.file_id))
      setProgress(30)
      setSuccess(`${response.data.total_files} file(s) uploaded successfully!`)
    } catch (err) {
      setError(`Upload failed: ${err.response?.data?.detail || err.message}`)
      setProgress(0)
    }
  }

  const handleAnalyze = async () => {
    if (uploadedFileIds.length === 0) {
      setError('Please upload files first')
      return
    }

    const estimatedMinutes = Math.ceil(uploadedFileIds.length * 1.5)
    const proceed = window.confirm(
      `Ready to analyze ${uploadedFileIds.length} paper${uploadedFileIds.length > 1 ? 's' : ''}.\n\n` +
        `Estimated time: ~${estimatedMinutes} minute${estimatedMinutes > 1 ? 's' : ''}.\n\n` +
        `Do you want to continue?`,
    )
    if (!proceed) return

    setAnalyzing(true)
    setError(null)
    setProgress(40)

    try {
      const startResponse = await axios.post(`${API_URL}/analyze`, uploadedFileIds, {
        timeout: 30000,
      })

      const jobId = startResponse.data.job_id
      setProgress(50)

      await new Promise((resolve, reject) => {
        let consecutiveErrors = 0
        const MAX_CONSECUTIVE_ERRORS = 5

        const interval = setInterval(async () => {
          try {
            const statusResponse = await axios.get(`${API_URL}/status/${jobId}`, {
              timeout: 15000,
            })
            consecutiveErrors = 0
            const { status, progress: done, total, excel_id, total_analyzed, error } =
              statusResponse.data

            if (total > 0) {
              setProgress(Math.round(50 + (done / total) * 40))
            }

            if (status === 'done') {
              clearInterval(interval)
              setProgress(100)
              setExcelId(excel_id)
              setSuccess(
                `Analysis complete! ${total_analyzed} paper(s) analyzed successfully.`,
              )
              setAnalyzing(false)
              resolve()
            } else if (status === 'failed') {
              clearInterval(interval)
              reject(new Error(error || 'Analysis failed on the server.'))
            }
          } catch (pollErr) {
            consecutiveErrors++
            if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
              clearInterval(interval)
              reject(pollErr)
            }
          }
        }, 5000)
      })
    } catch (err) {
      let errorMsg = 'Analysis failed: '
      if (err.code === 'ECONNABORTED') {
        errorMsg += 'Could not reach the server. Make sure the backend is running.'
      } else if (err.message.includes('Network Error')) {
        errorMsg += 'Network error. The backend might be starting up — please try again in a minute.'
      } else {
        errorMsg += err.response?.data?.detail || err.message
      }
      setError(errorMsg)
      setProgress(0)
      setAnalyzing(false)
    }
  }

  const handleDownload = () => {
    window.open(`${API_URL}/download/${excelId}`, '_blank')
  }

  const handleReset = () => {
    setFiles([])
    setUploadedFileIds([])
    setExcelId(null)
    setError(null)
    setSuccess(null)
    setProgress(0)
    setAnalyzing(false)
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <HeroSection />

        <Container maxWidth="md" sx={{ py: { xs: 3, md: 5 }, flex: 1 }}>
          {/* Stepper */}
          <Stepper
            activeStep={activeStep}
            alternativeLabel
            sx={{
              mb: 4,
              '& .MuiStepLabel-label': { fontWeight: 500, fontSize: '0.85rem' },
            }}
          >
            {STEPS.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Alerts */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
              {success}
            </Alert>
          )}

          {/* Download card (shown when analysis is complete) */}
          {excelId && (
            <Box sx={{ mb: 4 }}>
              <DownloadCard onDownload={handleDownload} onReset={handleReset} />
            </Box>
          )}

          {/* Upload section */}
          <Card sx={{ mb: 3 }}>
            <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 2,
                  flexWrap: 'wrap',
                  gap: 1,
                }}
              >
                <Box>
                  <Typography variant="h6" sx={{ mb: 0.25 }}>
                    Upload Research Papers
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Select one or more PDFs to analyze
                  </Typography>
                </Box>
                {files.length > 0 && !uploadedFileIds.length && (
                  <Box
                    component="button"
                    onClick={handleUpload}
                    disabled={analyzing}
                    sx={{
                      bgcolor: 'primary.main',
                      color: 'white',
                      border: 'none',
                      borderRadius: '10px',
                      px: 3,
                      py: 1.25,
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      cursor: analyzing ? 'default' : 'pointer',
                      opacity: analyzing ? 0.6 : 1,
                      fontFamily: 'inherit',
                      transition: 'background-color 0.2s',
                      '&:hover': analyzing ? {} : { bgcolor: 'primary.dark' },
                    }}
                  >
                    Upload {files.length} file{files.length > 1 ? 's' : ''}
                  </Box>
                )}
              </Box>
              <UploadZone
                files={files}
                onFilesSelected={handleFilesSelected}
                onRemoveFile={handleRemoveFile}
                disabled={analyzing || !!excelId}
              />
            </CardContent>
          </Card>

          {/* Analyze section */}
          <Card sx={{ mb: 3 }}>
            <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
              <Typography variant="h6" sx={{ mb: 0.25 }}>
                Run Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
                Process papers with GPT-4o to extract structured data
              </Typography>
              <AnalyzeSection
                uploadedCount={uploadedFileIds.length}
                analyzing={analyzing}
                excelId={excelId}
                progress={progress}
                onAnalyze={handleAnalyze}
              />
            </CardContent>
          </Card>

          {/* Extracted fields info */}
          <Card>
            <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
              <ExtractedFields />
            </CardContent>
          </Card>
        </Container>

        <Footer />
      </Box>
    </ThemeProvider>
  )
}

export default App
