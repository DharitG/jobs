import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Label } from './label'; // Adjust path as needed

describe('Label Component', () => {
  it('renders as a label element with children', () => {
    render(<Label htmlFor="test-input">Test Label</Label>);
    // Use getByText to find the label by its content
    const label = screen.getByText('Test Label'); 
    expect(label).toBeInTheDocument();
    expect(label.tagName.toLowerCase()).toBe('label');
    // Check if htmlFor is passed correctly
    expect(label).toHaveAttribute('for', 'test-input'); 
  });

  it('applies base styling classes', () => {
    render(<Label>Base Style Test</Label>);
    const label = screen.getByText('Base Style Test');
    // Check for a selection of key base classes
    expect(label).toHaveClass('text-sm');
    expect(label).toHaveClass('font-medium');
    expect(label).toHaveClass('leading-none');
    expect(label).toHaveClass('peer-disabled:cursor-not-allowed');
    expect(label).toHaveClass('peer-disabled:opacity-50');
  });

  it('applies additional className when provided', () => {
    const testClass = 'my-custom-label-class';
    render(<Label className={testClass}>Custom Class</Label>);
    const label = screen.getByText('Custom Class');
    expect(label).toHaveClass(testClass);
  });
});
