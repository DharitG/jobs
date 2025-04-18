import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { QuotaRing } from './QuotaRing'; // Adjust path as needed

describe('QuotaRing Component', () => {
  it('renders the remaining quota number correctly', () => {
    render(<QuotaRing remaining={35} total={50} />);
    const numberElement = screen.getByText('35');
    expect(numberElement).toBeInTheDocument();
    expect(numberElement.tagName.toLowerCase()).toBe('span');
  });

  it('calculates and applies the correct conic-gradient style', () => {
    const remaining = 10;
    const total = 50;
    const percentage = (remaining / total) * 100; // 20%
    render(<QuotaRing remaining={remaining} total={total} />);
    
    const ringElement = screen.getByTitle(`${remaining} / ${total} applications remaining`);
    expect(ringElement).toBeInTheDocument();
    expect(ringElement).toHaveStyle(
      `background: conic-gradient(#3E6DFF ${percentage}%, #E1E4F0 ${percentage}%)`
    );
  });

  it('handles zero total quota correctly (renders 0% gradient)', () => {
    render(<QuotaRing remaining={0} total={0} />);
    const ringElement = screen.getByTitle('0 / 0 applications remaining');
    expect(ringElement).toBeInTheDocument();
    expect(ringElement).toHaveStyle(
      'background: conic-gradient(#3E6DFF 0%, #E1E4F0 0%)'
    );
    expect(screen.getByText('0')).toBeInTheDocument();
  });
  
  it('handles remaining quota exceeding total (caps at 100%)', () => {
    render(<QuotaRing remaining={60} total={50} />);
    const ringElement = screen.getByTitle('60 / 50 applications remaining');
    expect(ringElement).toBeInTheDocument();
    expect(ringElement).toHaveStyle(
      'background: conic-gradient(#3E6DFF 100%, #E1E4F0 100%)'
    );
    expect(screen.getByText('60')).toBeInTheDocument(); // Still display actual remaining
  });

  it('handles negative remaining quota (clamps at 0%)', () => {
    render(<QuotaRing remaining={-5} total={50} />);
    const ringElement = screen.getByTitle('-5 / 50 applications remaining');
    expect(ringElement).toBeInTheDocument();
    expect(ringElement).toHaveStyle(
      'background: conic-gradient(#3E6DFF 0%, #E1E4F0 0%)'
    );
    expect(screen.getByText('-5')).toBeInTheDocument(); // Still display actual remaining
  });

  it('applies default dimensions correctly', () => {
    const defaultSize = 40;
    const defaultStroke = 4;
    render(<QuotaRing remaining={25} total={50} />);
    const ringElement = screen.getByTitle('25 / 50 applications remaining');
    const innerCircle = ringElement.firstChild as HTMLElement;

    expect(ringElement).toHaveStyle(`width: ${defaultSize}px`);
    expect(ringElement).toHaveStyle(`height: ${defaultSize}px`);
    expect(innerCircle).toHaveStyle(`width: ${defaultSize - defaultStroke * 2}px`);
    expect(innerCircle).toHaveStyle(`height: ${defaultSize - defaultStroke * 2}px`);
  });

  it('applies custom dimensions correctly', () => {
    const customSize = 60;
    const customStroke = 6;
    render(<QuotaRing remaining={25} total={50} size={customSize} strokeWidth={customStroke} />);
    const ringElement = screen.getByTitle('25 / 50 applications remaining');
    const innerCircle = ringElement.firstChild as HTMLElement;

    expect(ringElement).toHaveStyle(`width: ${customSize}px`);
    expect(ringElement).toHaveStyle(`height: ${customSize}px`);
    expect(innerCircle).toHaveStyle(`width: ${customSize - customStroke * 2}px`);
    expect(innerCircle).toHaveStyle(`height: ${customSize - customStroke * 2}px`);
  });

  it('renders the correct title attribute', () => {
    render(<QuotaRing remaining={15} total={30} />);
    expect(screen.getByTitle('15 / 30 applications remaining')).toBeInTheDocument();
  });
});
