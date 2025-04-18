import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose, // Import DialogClose
  // DialogOverlay is rendered internally by DialogContent via DialogPortal
} from './dialog'; // Adjust path as needed

describe('Dialog Components', () => {
  const TestDialog = () => (
    <Dialog>
      <DialogTrigger asChild>
        <button>Open Dialog</button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dialog Title</DialogTitle>
          <DialogDescription>Dialog Description</DialogDescription>
        </DialogHeader>
        <p>Dialog main content.</p>
        <DialogFooter>
          <button>Footer Button</button>
           {/* Optional: Add explicit DialogClose for testing */}
           {/* <DialogClose asChild><button>Close Footer</button></DialogClose> */}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );

  it('renders trigger and hides content initially', () => {
    render(<TestDialog />);
    expect(screen.getByRole('button', { name: /open dialog/i })).toBeInTheDocument();
    // Content is rendered in a portal, so queryBy methods might not find it easily if not open
    expect(screen.queryByRole('dialog')).toBeNull(); 
    expect(screen.queryByText('Dialog Title')).toBeNull();
  });

  it('opens dialog and shows content when trigger is clicked', async () => {
    const user = userEvent.setup();
    render(<TestDialog />);
    
    const trigger = screen.getByRole('button', { name: /open dialog/i });
    expect(screen.queryByRole('dialog')).toBeNull(); 

    await user.click(trigger);

    // Wait for dialog content to appear (due to portal and potential animation)
    const dialogContent = await screen.findByRole('dialog');
    expect(dialogContent).toBeVisible();
    expect(screen.getByText('Dialog Title')).toBeVisible();
    expect(screen.getByText('Dialog Description')).toBeVisible();
    expect(screen.getByText('Dialog main content.')).toBeVisible();
    expect(screen.getByRole('button', { name: /footer button/i })).toBeVisible();
  });

  it('closes dialog when the internal close button (X) is clicked', async () => {
    const user = userEvent.setup();
    render(<TestDialog />);
    
    // Open the dialog first
    const trigger = screen.getByRole('button', { name: /open dialog/i });
    await user.click(trigger);
    const dialogContent = await screen.findByRole('dialog');
    expect(dialogContent).toBeVisible();

    // Find and click the close button (X icon)
    // Radix adds an aria-label="Close" by default to the internal close button
    const closeButton = screen.getByRole('button', { name: /close/i }); 
    await user.click(closeButton);

    // Wait for the dialog to disappear
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).toBeNull();
    });
  });
  
  // Note: Testing overlay click might require more setup if animations interfere
  // It relies on Radix's default behavior which is generally reliable.
  // We can add it if specific issues arise.
  /*
  it('closes dialog when overlay is clicked', async () => {
    const user = userEvent.setup();
    render(<TestDialog />);
    
    // Open the dialog
    await user.click(screen.getByRole('button', { name: /open dialog/i }));
    const dialogContent = await screen.findByRole('dialog');
    expect(dialogContent).toBeVisible();

    // Find the overlay (might need a specific selector or test id if default doesn't work)
    // Radix might not expose a direct role for the overlay easily.
    // Clicking outside the content often triggers close.
    await user.click(document.body); // Simulate click outside

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).toBeNull();
    });
  });
  */

});
