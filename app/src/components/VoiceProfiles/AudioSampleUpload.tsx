import { FileVideo, Mic, Pause, Play, Upload } from 'lucide-react';
import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { FormControl, FormItem, FormMessage } from '@/components/ui/form';
import { isVideoFile } from '@/lib/utils/audio';

interface AudioSampleUploadProps {
  file: File | null | undefined;
  onFileChange: (file: File | undefined) => void;
  onTranscribe: () => void;
  onPlayPause: () => void;
  isPlaying: boolean;
  isValidating?: boolean;
  isTranscribing?: boolean;
  isDisabled?: boolean;
  fieldName: string;
  uploadProgress?: number;
}

export function AudioSampleUpload({
  file,
  onFileChange,
  onTranscribe,
  onPlayPause,
  isPlaying,
  isValidating = false,
  isTranscribing = false,
  isDisabled = false,
  fieldName,
  uploadProgress,
}: AudioSampleUploadProps) {
  const { t } = useTranslation();
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <FormItem>
      <FormControl>
        <div className="flex flex-col gap-2">
          <input
            type="file"
            accept="audio/*,video/*"
            name={fieldName}
            ref={fileInputRef}
            onChange={(e) => {
              const selectedFile = e.target.files?.[0];
              if (selectedFile) {
                onFileChange(selectedFile);
              } else {
                onFileChange(undefined);
              }
            }}
            className="hidden"
          />
          <div
            role="button"
            tabIndex={0}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              setIsDragging(false);
            }}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragging(false);
              const droppedFile = e.dataTransfer.files?.[0];
              if (
                droppedFile &&
                (droppedFile.type.startsWith('audio/') ||
                  isVideoFile(droppedFile.name, droppedFile.type))
              ) {
                onFileChange(droppedFile);
              }
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInputRef.current?.click();
              }
            }}
            className={`flex flex-col items-center justify-center gap-4 p-4 border-2 rounded-lg transition-colors min-h-[180px] ${
              file
                ? 'border-primary bg-primary/5'
                : isDragging
                  ? 'border-primary bg-primary/5'
                  : 'border-dashed border-muted-foreground/25 hover:border-muted-foreground/50'
            }`}
          >
            {!file ? (
              <>
                <Button
                  type="button"
                  size="lg"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center gap-2"
                >
                  <Upload className="h-5 w-5" />
                  {t('audioSample.chooseFile')}
                </Button>
                <p className="text-sm text-muted-foreground text-center">
                  {t('audioSample.uploadHint')}
                </p>
                <p className="text-xs text-muted-foreground/80 text-center">
                  {t('audioSample.videoHint')}
                </p>
              </>
            ) : (
              <>
                <div className="flex items-center gap-2">
                  {isVideoFile(file.name, file.type) ? (
                    <FileVideo className="h-5 w-5 text-primary" />
                  ) : (
                    <Upload className="h-5 w-5 text-primary" />
                  )}
                  <span className="font-medium">{t('audioSample.fileUploaded')}</span>
                </div>
                <p className="text-sm text-muted-foreground text-center">
                  {t('audioSample.fileLabel', { name: file.name })}
                </p>
                {uploadProgress !== undefined && uploadProgress > 0 && (
                  <div className="w-full max-w-sm space-y-1" aria-live="polite">
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>
                        {uploadProgress < 100
                          ? t('audioSample.uploading')
                          : t('audioSample.uploadComplete')}
                      </span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary transition-[width] duration-150"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}
                <div className="flex gap-2">
                  <Button
                    type="button"
                    size="icon"
                    variant="outline"
                    onClick={onPlayPause}
                    disabled={isValidating}
                    aria-label={isPlaying ? t('audioSample.pause') : t('audioSample.play')}
                  >
                    {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={onTranscribe}
                    disabled={isTranscribing || isValidating || isDisabled}
                    className="flex items-center gap-2"
                  >
                    <Mic className="h-4 w-4" />
                    {isTranscribing ? t('audioSample.transcribing') : t('audioSample.transcribe')}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      onFileChange(undefined);
                      if (fileInputRef.current) {
                        fileInputRef.current.value = '';
                      }
                    }}
                  >
                    {t('audioSample.remove')}
                  </Button>
                </div>
              </>
            )}
          </div>
        </div>
      </FormControl>
      <FormMessage />
    </FormItem>
  );
}
