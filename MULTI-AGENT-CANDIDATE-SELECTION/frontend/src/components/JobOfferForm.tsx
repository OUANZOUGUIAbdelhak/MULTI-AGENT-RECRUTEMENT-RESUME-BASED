import { motion } from 'framer-motion';
import { Briefcase, FileText, Upload, X } from 'lucide-react';
import { useState, useRef } from 'react';
import { JobOffer } from '../types';
import { parseJobOfferFile } from '../utils/jobOfferParser';
import { cn } from '../utils/cn';

interface JobOfferFormProps {
  onJobOfferChange: (offer: JobOffer | null) => void;
  initialOffer?: JobOffer | null;
}

export default function JobOfferForm({ onJobOfferChange, initialOffer }: JobOfferFormProps) {
  const [jobOffer, setJobOffer] = useState<JobOffer>(
    initialOffer || {
      title: '',
      description: '',
      requirements: '',
      location: '',
      salary: '',
    }
  );
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = (field: keyof JobOffer, value: string) => {
    const updated = { ...jobOffer, [field]: value };
    setJobOffer(updated);
    onJobOfferChange(
      updated.title && updated.description && updated.requirements ? updated : null
    );
  };

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setUploadedFileName(file.name);

    try {
      // Read text file
      const text = await file.text();
      const parsed = parseJobOfferFile(text, file.name);
      
      setJobOffer(parsed);
      onJobOfferChange(
        parsed.title && parsed.description && parsed.requirements ? parsed : null
      );
    } catch (error) {
      console.error('Error parsing job offer file:', error);
      alert('Error reading file. Please ensure it is a valid text file and try again.');
      setUploadedFileName(null);
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFileName(null);
    setJobOffer({
      title: '',
      description: '',
      requirements: '',
      location: '',
      salary: '',
    });
    onJobOfferChange(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20">
            <Briefcase className="w-6 h-6 text-blue-400" />
          </div>
          <h2 className="text-2xl font-bold text-white">Job Offer Details</h2>
        </div>
      </div>

      {/* File Upload Section */}
      <div className="mb-6">
        <div className="flex items-center gap-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt"
            onChange={handleFileSelect}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl border transition-all',
              'bg-white/5 border-white/20 hover:border-blue-400/50 hover:bg-blue-500/10',
              'text-white disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            <Upload className="w-4 h-4" />
            <span className="text-sm font-medium">
              {isUploading ? 'Uploading...' : 'Upload Job Offer File'}
            </span>
          </button>
          {uploadedFileName && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/10 border border-green-400/20">
              <FileText className="w-4 h-4 text-green-400" />
              <span className="text-sm text-green-400 font-medium truncate max-w-[200px]">
                {uploadedFileName}
              </span>
              <button
                onClick={handleRemoveFile}
                className="p-1 rounded hover:bg-red-500/20 text-red-400 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Upload a .txt file containing the job offer description. The form will be auto-filled with extracted information.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Job Title <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={jobOffer.title}
            onChange={(e) => handleChange('title', e.target.value)}
            placeholder="e.g., Senior Data Scientist"
            className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Job Description <span className="text-red-400">*</span>
          </label>
          <textarea
            value={jobOffer.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Describe the role, responsibilities, and what you're looking for..."
            rows={5}
            className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Requirements <span className="text-red-400">*</span>
          </label>
          <textarea
            value={jobOffer.requirements}
            onChange={(e) => handleChange('requirements', e.target.value)}
            placeholder="List required skills, experience, education, certifications..."
            rows={4}
            className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all resize-none"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Location (Optional)
            </label>
            <input
              type="text"
              value={jobOffer.location || ''}
              onChange={(e) => handleChange('location', e.target.value)}
              placeholder="e.g., Paris, France / Remote"
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Salary Range (Optional)
            </label>
            <input
              type="text"
              value={jobOffer.salary || ''}
              onChange={(e) => handleChange('salary', e.target.value)}
              placeholder="e.g., €50k - €70k"
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
            />
          </div>
        </div>

        {jobOffer.title && jobOffer.description && jobOffer.requirements && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 p-3 rounded-xl bg-green-500/10 border border-green-400/20"
          >
            <FileText className="w-5 h-5 text-green-400" />
            <span className="text-sm text-green-400 font-medium">
              Job offer is ready for evaluation
            </span>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

