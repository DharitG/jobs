"use client";

import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogClose } from "~/components/ui/dialog"; // Assuming DialogClose is available or create one
import { X } from 'lucide-react'; // Import X icon for close button

interface VideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoSrc: string; // Expecting a direct video source URL
  title?: string; // Optional title
}

export function VideoModal({
  isOpen,
  onClose,
  videoSrc,
  title = "OpenCrew Demo", // Updated default title
}: VideoModalProps) {
  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl p-0"> {/* Adjust max-width and remove padding */}
        <DialogHeader className="p-4 border-b border-grey-20 flex flex-row items-center justify-between">
          <DialogTitle className="text-lg font-semibold">{title}</DialogTitle>
          <DialogClose asChild>
            <button
              onClick={onClose}
              className="p-1 rounded-full text-grey-40 hover:bg-grey-10 hover:text-grey-90 transition-colors"
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </DialogClose>
        </DialogHeader>
        {/* Video Player */}
        <div className="aspect-video"> {/* Maintain 16:9 aspect ratio */}
          <video
            src={videoSrc}
            controls // Show default video controls
            autoPlay // Start playing automatically
            className="w-full h-full"
          >
            Your browser does not support the video tag.
          </video>
        </div>
      </DialogContent>
    </Dialog>
  );
}
