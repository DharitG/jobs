import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ProgressMeter } from './ProgressMeter'; // Adjust path as needed

// Define stages for testing consistency
const stages = ['Applied', 'Screening', 'Interview', 'Offer'] as const;
type ApplicationStage = typeof stages[number] | 'Rejected';

describe('ProgressMeter Component', () => {
  // Test each standard stage for correct percentage width and primary color
  stages.forEach((stage, index) => {
    const expectedPercentage = ((index + 1) / stages.length) * 100;

    it(`renders correctly for stage: ${stage}`, () => {
      render(<ProgressMeter currentStage={stage} />);

      // Check title attribute
      const progressBarContainer = screen.getByTitle(`Current Stage: ${stage}`);
      expect(progressBarContainer).toBeInTheDocument();

      // Check the inner div (the actual progress bar) for style and class using data-testid
      const progressBarInner = screen.getByTestId('progress-bar-inner');
      expect(progressBarInner).toBeInTheDocument();
      expect(progressBarInner).toHaveStyle(`width: ${expectedPercentage}%`);
      expect(progressBarInner).toHaveClass('bg-primary-500');
      expect(progressBarInner).not.toHaveClass('bg-error');
    });
  });

  // Test the 'Rejected' stage specifically
  it('renders correctly for stage: Rejected', () => {
    const stage: ApplicationStage = 'Rejected';
    render(<ProgressMeter currentStage={stage} />);

    // Check title attribute
    const progressBarContainer = screen.getByTitle(`Current Stage: ${stage}`);
      expect(progressBarContainer).toBeInTheDocument();

      // Check the inner div (the actual progress bar) for style and class using data-testid
      const progressBarInner = screen.getByTestId('progress-bar-inner');
      expect(progressBarInner).toBeInTheDocument();
      expect(progressBarInner).toHaveStyle('width: 0%'); // Rejected should show 0% progress visually
    expect(progressBarInner).toHaveClass('bg-error');
    expect(progressBarInner).not.toHaveClass('bg-primary-500');
  });

  // Test handling of potentially invalid stage (should default to 0%)
  it('renders with 0% width for an unknown stage', () => {
    // Cast to bypass type safety for testing invalid input
    const invalidStage = 'UnknownStage' as ApplicationStage; 
    render(<ProgressMeter currentStage={invalidStage} />);

    const progressBarContainer = screen.getByTitle(`Current Stage: ${invalidStage}`);
      expect(progressBarContainer).toBeInTheDocument();

      // Check the inner div (the actual progress bar) for style and class using data-testid
      const progressBarInner = screen.getByTestId('progress-bar-inner');
      expect(progressBarInner).toBeInTheDocument();
      expect(progressBarInner).toHaveStyle('width: 0%');
    // Should still use primary color unless explicitly rejected
    expect(progressBarInner).toHaveClass('bg-primary-500'); 
  });

  // Test className propagation
  it('applies additional className when provided', () => {
    const testClass = 'my-custom-class';
    render(<ProgressMeter currentStage="Interview" className={testClass} />);
    
    const progressBarContainer = screen.getByTitle('Current Stage: Interview');
    expect(progressBarContainer).toHaveClass(testClass);
  });
});
