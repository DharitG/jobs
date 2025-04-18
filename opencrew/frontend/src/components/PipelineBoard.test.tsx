import { render, screen, within } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PipelineBoard } from './PipelineBoard'; // Adjust path as needed
import { api } from '~/trpc/react'; // Import the mocked api
import { useToast } from '~/hooks/use-toast'; // Import the mocked hook

// Mock JobCard to simplify testing the board structure
vi.mock('./JobCard', () => ({
  JobCard: (props: any) => (
    <div data-testid={`job-card-${props.id}`}>
      {props.companyName} - {props.jobTitle}
    </div>
  ),
}));

// Mock dnd-kit context and hooks
vi.mock('@dnd-kit/core', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@dnd-kit/core')>();
  return {
    ...actual,
    DndContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>, // Render children directly
    useSensor: vi.fn(),
    useSensors: vi.fn(),
  };
});
vi.mock('@dnd-kit/sortable', () => ({
  SortableContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>, // Render children directly
  verticalListSortingStrategy: vi.fn(),
  arrayMove: vi.fn((arr) => arr), // Return original array for simplicity
  sortableKeyboardCoordinates: vi.fn(), // Add the missing mock export
}));

// Mock tRPC mutation and utils
vi.mock('~/trpc/react', () => ({
  api: {
    application: {
      updateStatus: {
        useMutation: vi.fn(() => ({ // Mock the hook itself
          mutate: vi.fn(), // Mock the mutate function
          // Add other properties if needed by the component (isLoading, isError, etc.)
        })),
      },
    },
     // Mock useUtils if its methods are called directly (e.g., invalidate)
    useUtils: vi.fn(() => ({
      application: {
        list: {
          invalidate: vi.fn(),
          // setData: vi.fn(), // Mock if setData is used
        },
      },
    })),
  },
}));

// Mock useToast hook
vi.mock('~/hooks/use-toast', () => ({
  useToast: vi.fn(() => ({
    toast: vi.fn(), // Mock the toast function
  })),
}));

// Define ApplicationItem type matching the component's expectation
type ApplicationStage = 'Applied' | 'Screening' | 'Interview' | 'Offer' | 'Rejected';
interface ApplicationItem {
  id: string | number;
  companyName: string;
  jobTitle: string;
  location?: string | null;
  stage: ApplicationStage;
  logoUrl?: string;
  ctaLink?: string;
}

// Sample data with explicit type
const sampleApplications: ApplicationItem[] = [
  { id: 'app-1', companyName: 'Comp A', jobTitle: 'Dev', stage: 'Applied', location: 'City A' },
  { id: 'app-2', companyName: 'Comp B', jobTitle: 'Eng', stage: 'Applied', location: 'City B' },
  { id: 'app-3', companyName: 'Comp C', jobTitle: 'Mgr', stage: 'Interview', location: 'City C' },
  { id: 'app-4', companyName: 'Comp D', jobTitle: 'QA', stage: 'Offer', location: 'City D' },
];

const pipelineStages = ['Applied', 'Screening', 'Interview', 'Offer'];

describe('PipelineBoard Component', () => {
  it('renders all defined pipeline stage columns', () => {
    render(<PipelineBoard initialApplications={[]} />);
    pipelineStages.forEach(stage => {
      // Check for column header text
      expect(screen.getByText(stage)).toBeInTheDocument(); 
    });
  });

  it('renders the correct number of job cards in each column', () => {
    render(<PipelineBoard initialApplications={sampleApplications} />);
    
    // Check 'Applied' column using data-testid
    const appliedColumn = screen.getByTestId('pipeline-column-Applied');
    expect(within(appliedColumn).getAllByTestId(/job-card-/)).toHaveLength(2);
    expect(within(appliedColumn).getByText('Comp A - Dev')).toBeInTheDocument();
    expect(within(appliedColumn!).getByText('Comp B - Eng')).toBeInTheDocument();

    // Check 'Screening' column (should be empty) using data-testid
    const screeningColumn = screen.getByTestId('pipeline-column-Screening');
    expect(within(screeningColumn).queryAllByTestId(/job-card-/)).toHaveLength(0);

    // Check 'Interview' column using data-testid
    const interviewColumn = screen.getByTestId('pipeline-column-Interview');
    expect(within(interviewColumn).getAllByTestId(/job-card-/)).toHaveLength(1);
    expect(within(interviewColumn).getByText('Comp C - Mgr')).toBeInTheDocument();
    
    // Check 'Offer' column using data-testid
    const offerColumn = screen.getByTestId('pipeline-column-Offer');
     expect(within(offerColumn).getAllByTestId(/job-card-/)).toHaveLength(1);
     expect(within(offerColumn).getByText('Comp D - QA')).toBeInTheDocument();
  });

  it('displays the correct count in each column header badge', () => {
    render(<PipelineBoard initialApplications={sampleApplications} />);
    
    // Check counts within the correct column using data-testid
    const appliedColumn = screen.getByTestId('pipeline-column-Applied');
    expect(within(appliedColumn).getByText('2')).toBeInTheDocument(); // Count for Applied

    const screeningColumn = screen.getByTestId('pipeline-column-Screening');
    expect(within(screeningColumn).getByText('0')).toBeInTheDocument(); // Count for Screening

    const interviewColumn = screen.getByTestId('pipeline-column-Interview');
    expect(within(interviewColumn).getByText('1')).toBeInTheDocument(); // Count for Interview

    const offerColumn = screen.getByTestId('pipeline-column-Offer');
    expect(within(offerColumn).getByText('1')).toBeInTheDocument(); // Count for Offer
  });

  it('displays "Drop jobs here" message in empty columns', () => {
    render(<PipelineBoard initialApplications={[]} />); // Start with no applications
    
    // Check the empty state 
    pipelineStages.forEach(stage => {
      const column = screen.getByTestId(`pipeline-column-${stage}`);
      expect(within(column).getByText('Drop jobs here')).toBeInTheDocument();
    });
    // Removed the rerender and subsequent check for this test case
  });
});
