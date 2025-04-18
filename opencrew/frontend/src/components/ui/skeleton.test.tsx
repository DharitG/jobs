import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Skeleton } from './skeleton'; // Adjust path as needed

describe('Skeleton Component', () => {
  it('renders as a div element', () => {
    render(<Skeleton data-testid="skeleton-test" />);
    const skeleton = screen.getByTestId('skeleton-test');
    expect(skeleton).toBeInTheDocument();
    expect(skeleton.tagName.toLowerCase()).toBe('div');
  });

  it('applies base styling classes', () => {
    render(<Skeleton data-testid="skeleton-test" />);
    const skeleton = screen.getByTestId('skeleton-test');
    // Check for key base classes
    expect(skeleton).toHaveClass('bg-accent');
    expect(skeleton).toHaveClass('animate-pulse');
    expect(skeleton).toHaveClass('rounded-md');
  });

  it('applies additional className when provided', () => {
    const testClass = 'my-custom-skeleton-class';
    render(<Skeleton data-testid="skeleton-test" className={testClass} />);
    const skeleton = screen.getByTestId('skeleton-test');
    expect(skeleton).toHaveClass(testClass);
  });

  it('forwards other div props correctly', () => {
    render(<Skeleton data-testid="skeleton-test" id="skeleton-id" title="Loading..." />);
    const skeleton = screen.getByTestId('skeleton-test');
    expect(skeleton).toHaveAttribute('id', 'skeleton-id');
    expect(skeleton).toHaveAttribute('title', 'Loading...');
  });
});
