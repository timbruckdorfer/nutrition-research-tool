import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Chip,
} from '@mui/material'
import { CloudUpload, Description, Close } from '@mui/icons-material'

export default function UploadZone({ files, onFilesSelected, onRemoveFile, disabled }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      onFilesSelected(acceptedFiles)
    },
    [onFilesSelected],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    disabled,
    multiple: true,
  })

  return (
    <Box>
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.200',
          borderRadius: 3,
          p: { xs: 3, md: 5 },
          textAlign: 'center',
          cursor: disabled ? 'default' : 'pointer',
          bgcolor: isDragActive ? 'rgba(46,125,50,0.04)' : 'grey.50',
          transition: 'all 0.2s ease',
          '&:hover': disabled
            ? {}
            : {
                borderColor: 'primary.light',
                bgcolor: 'rgba(46,125,50,0.02)',
              },
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload
          sx={{
            fontSize: 44,
            color: isDragActive ? 'primary.main' : 'grey.400',
            mb: 1.5,
            transition: 'color 0.2s ease',
          }}
        />
        <Typography variant="subtitle1" sx={{ color: 'text.primary', mb: 0.5 }}>
          {isDragActive ? 'Drop your PDFs here' : 'Drag & drop PDF files here'}
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          or click to browse your files
        </Typography>
      </Box>

      {files.length > 0 && (
        <List sx={{ mt: 2 }}>
          {files.map((file, index) => (
            <ListItem
              key={index}
              sx={{
                bgcolor: 'grey.50',
                borderRadius: 2,
                mb: 0.5,
                pr: 1,
              }}
              secondaryAction={
                !disabled && (
                  <IconButton
                    edge="end"
                    size="small"
                    onClick={() => onRemoveFile(index)}
                  >
                    <Close fontSize="small" />
                  </IconButton>
                )
              }
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <Description sx={{ color: 'primary.main' }} />
              </ListItemIcon>
              <ListItemText
                primary={file.name}
                secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  )
}
