"use client";

import React, { useState, useRef, useEffect } from "react";
import { X } from "lucide-react";

interface StudentAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (registerNo: string, kpPassword: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

/**
 * Level 2 Authentication Modal for Knowledge Pro Student Portal
 * 
 * Handles Register Number and KP Password authentication for Christ University
 * Knowledge Pro portal. Includes validation, loading states, and error handling.
 */
export function StudentAuthModal({
  isOpen,
  onClose,
  onLogin,
  isLoading = false,
  error = null,
}: StudentAuthModalProps) {
  const [registerNo, setRegisterNo] = useState("");
  const [kpPassword, setKpPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ registerNo?: string; kpPassword?: string }>({});
  
  const modalRef = useRef<HTMLDivElement>(null);
  const registerNoRef = useRef<HTMLInputElement>(null);

  // Focus register number input when modal opens
  useEffect(() => {
    if (isOpen && registerNoRef.current) {
      registerNoRef.current.focus();
    }
  }, [isOpen]);

  // Clear errors when user starts typing
  useEffect(() => {
    if (registerNo) setFieldErrors(prev => ({ ...prev, registerNo: undefined }));
  }, [registerNo]);

  useEffect(() => {
    if (kpPassword) setFieldErrors(prev => ({ ...prev, kpPassword: undefined }));
  }, [kpPassword]);

  // Handle escape key to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  const validateForm = (): boolean => {
    const errors: { registerNo?: string; kpPassword?: string } = {};
    
    if (!registerNo.trim()) {
      errors.registerNo = "Register number is required";
    } else if (!/^\d{7,}$/.test(registerNo.trim())) {
      errors.registerNo = "Enter a valid 7+ digit register number";
    }
    
    if (!kpPassword) {
      errors.kpPassword = "KP password is required";
    } else if (kpPassword.length < 4) {
      errors.kpPassword = "Password must be at least 4 characters";
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await onLogin(registerNo.trim(), kpPassword);
    } catch (err) {
      // Error is handled by parent component via error prop
      console.error("Login failed:", err);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className="w-full max-w-md bg-white dark:bg-gray-800 rounded-xl shadow-2xl animate-slide-up overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 id="modal-title" className="text-lg font-semibold text-gray-900 dark:text-white">
            Knowledge Pro Portal Login
          </h2>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="p-1 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Info badge */}
          <div className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Level 2 Authentication: Register No + KP Password</span>
          </div>

          {/* Register Number Field */}
          <div>
            <label
              htmlFor="registerNo"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Register Number <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                ref={registerNoRef}
                id="registerNo"
                type="text"
                value={registerNo}
                onChange={(e) => setRegisterNo(e.target.value)}
                placeholder="e.g., 22BCE1234"
                className={`w-full px-4 py-2.5 rounded-lg border transition-colors ${
                  fieldErrors.registerNo
                    ? "border-red-500 focus:ring-red-500 focus:border-red-500"
                    : "border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500"
                } bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400`}
                disabled={isLoading}
                autoComplete="username"
                aria-invalid={fieldErrors.registerNo ? "true" : "false"}
                aria-describedby={fieldErrors.registerNo ? "registerNo-error" : undefined}
              />
              <div className="absolute inset-0 flex items-center justify-end px-3 pointer-events-none">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            </div>
            {fieldErrors.registerNo && (
              <p id="registerNo-error" className="mt-1 text-sm text-red-500" role="alert">
                {fieldErrors.registerNo}
              </p>
            )}
          </div>

          {/* KP Password Field */}
          <div>
            <label
              htmlFor="kpPassword"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              KP Password <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                id="kpPassword"
                type={showPassword ? "text" : "password"}
                value={kpPassword}
                onChange={(e) => setKpPassword(e.target.value)}
                placeholder="Enter your KP portal password"
                className={`w-full px-4 py-2.5 rounded-lg border transition-colors pr-12 ${
                  fieldErrors.kpPassword
                    ? "border-red-500 focus:ring-red-500 focus:border-red-500"
                    : "border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500"
                } bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400`}
                disabled={isLoading}
                autoComplete="current-password"
                aria-invalid={fieldErrors.kpPassword ? "true" : "false"}
                aria-describedby={fieldErrors.kpPassword ? "kpPassword-error" : undefined}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
            {fieldErrors.kpPassword && (
              <p id="kpPassword-error" className="mt-1 text-sm text-red-500" role="alert">
                {fieldErrors.kpPassword}
              </p>
            )}
          </div>

          {/* Error Message from Parent */}
          {error && (
            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800" role="alert">
              <div className="flex items-center gap-2 text-sm text-red-700 dark:text-red-300">
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Authenticating...
              </>
            ) : (
              "Login to KP Portal"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Your credentials are used only to authenticate with Christ University's
            Knowledge Pro portal. They are never stored or shared.
          </p>
        </div>
      </div>
    </div>
  );
}

export default StudentAuthModal;