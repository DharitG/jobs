'use client';

import React, { useState } from 'react';
import { Button } from '~/components/ui/button';
// Corrected imports for shadcn/ui components
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from '~/components/ui/dialog'; // Correct path for Dialog components
import { Textarea } from '~/components/ui/textarea'; // Correct path for Textarea
import { Loader2 } from 'lucide-react';
import { useToast } from '~/hooks/use-toast';
// TODO: Import tRPC hook when backend procedure is ready
// import { api } from '~/trpc/react';

interface ResumeEditModalProps {
  resumeText: string; // Pass the current resume text
  onSaveChanges?: (updatedText: string) => void; // Callback when changes are saved (optional) - Made optional
  triggerButton?: React.ReactNode; // Allow custom trigger button
}

export function ResumeEditModal({
  resumeText,
  onSaveChanges,
  triggerButton
}: ResumeEditModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [editedText, setEditedText] = useState(resumeText);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  // TODO: Implement tRPC mutation for GPT edit
  // const editMutation = api.resume.editWithGPT.useMutation({ ... });

  const handleEditClick = () => {
    setIsLoading(true);
    console.log("Triggering GPT resume edit for:", editedText.substring(0, 50) + "...");
    // Placeholder for API call
    // editMutation.mutate({ resumeText: editedText }, {
    //   onSuccess: (data) => {
    //     setEditedText(data.editedResume); // Assuming backend returns edited text
    //     toast({ title: "Resume Enhanced", description: "GPT suggestions applied." });
    //     setIsLoading(false);
    //   },
    //   onError: (error) => {
    //     toast({ title: "Edit Failed", description: error.message, variant: "destructive" });
    //     setIsLoading(false);
    //   }
    // });

    // Simulate API call for now
    setTimeout(() => {
      setEditedText(editedText + "\n\n[GPT Edit Placeholder: Improved phrasing.]");
      toast({ title: "Resume Enhanced (Mock)", description: "GPT suggestions applied." });
      setIsLoading(false);
    }, 1500);
  };

  const handleSave = () => {
    console.log("Saving edited resume...");
    if (onSaveChanges) {
      onSaveChanges(editedText);
    }
    setIsOpen(false); // Close modal on save
    toast({ title: "Changes Saved", description: "Your resume has been updated." });
  };

  // Reset edited text when modal opens
  React.useEffect(() => {
    if (isOpen) {
      setEditedText(resumeText);
    }
  }, [isOpen, resumeText]);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {triggerButton ? triggerButton : <Button variant="outline">Edit Resume with AI</Button>}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Enhance Resume with AI</DialogTitle>
          <DialogDescription>
            Use AI to improve phrasing and keywords in your resume. Free tier includes limited edits.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <Textarea
            value={editedText}
            // Add type to event parameter
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setEditedText(e.target.value)}
            rows={15}
            placeholder="Paste or load your resume text here..."
            className="min-h-[300px]" // Ensure decent height
          />
          <Button onClick={handleEditClick} disabled={isLoading}>
            {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            {isLoading ? 'Enhancing...' : 'Enhance with AI'}
          </Button>
        </div>
        <DialogFooter>
          <DialogClose asChild>
             <Button type="button" variant="secondary">
               Cancel
             </Button>
          </DialogClose>
          <Button type="button" onClick={handleSave} disabled={isLoading}>
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
