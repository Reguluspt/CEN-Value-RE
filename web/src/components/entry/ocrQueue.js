const IMAGE_FILE_PATTERN = /\.(png|jpe?g|webp)$/i;

export const isMergedImageSource = (file, batchFiles = []) => (
  batchFiles.some((candidate) => candidate.merged_from_images)
  && IMAGE_FILE_PATTERN.test(String(file?.name || ''))
);

export const initialScanStatus = (file, batchFiles = []) => (
  isMergedImageSource(file, batchFiles) ? 'skipped' : 'pending'
);
