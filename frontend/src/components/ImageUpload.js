import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon } from 'lucide-react';

const ImageUpload = ({ onImageUpload, isUploading }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onImageUpload(acceptedFiles[0]);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
    disabled: isUploading
  });

  return (
    <div
      {...getRootProps()}
      className={`
        dropzone p-8 border-2 border-dashed rounded-lg cursor-pointer transition-colors
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />
      <div className="text-center">
        <div className="flex justify-center mb-4">
          {isUploading ? (
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          ) : (
            <ImageIcon className="h-12 w-12 text-gray-400" />
          )}
        </div>
        
        {isDragActive ? (
          <p className="text-blue-600 font-medium">Drop the image here...</p>
        ) : (
          <div>
            <p className="text-gray-600 mb-2">
              <span className="font-medium">Click to upload</span> or drag and drop
            </p>
            <p className="text-sm text-gray-500">
              PNG, JPG, JPEG, WEBP up to 10MB
            </p>
          </div>
        )}
        
        <div className="mt-4 flex justify-center">
          <Upload className="h-5 w-5 text-gray-400" />
        </div>
      </div>
    </div>
  );
};

export default ImageUpload;
