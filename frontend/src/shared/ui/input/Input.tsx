import React from 'react';
import './Input.css';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'filled' | 'outlined';
}

export function Input({
  label,
  error,
  helperText,
  variant = 'default',
  className = '',
  id,
  ...props
}: InputProps) {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  const baseClasses = 'input';
  const variantClasses = `input--${variant}`;
  const errorClasses = error ? 'input--error' : '';

  const classes = [
    baseClasses,
    variantClasses,
    errorClasses,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="input-wrapper">
      {label && (
        <label htmlFor={inputId} className="input-label">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={classes}
        {...props}
      />
      {error && (
        <span className="input-error">
          {error}
        </span>
      )}
      {helperText && !error && (
        <span className="input-helper">
          {helperText}
        </span>
      )}
    </div>
  );
}
