"use client";

import Image from "next/image";
import { useState } from "react";

interface ProfileAvatarProps {
  showImage: boolean;
}

export function ProfileAvatar({ showImage }: ProfileAvatarProps) {
  const [imageReady, setImageReady] = useState(false);
  const [imageFailed, setImageFailed] = useState(false);

  return (
    <div className="relative flex aspect-square w-32 shrink-0 items-center justify-center overflow-hidden rounded-md border border-border bg-accent text-5xl font-semibold text-primary shadow-soft sm:w-40">
      <span aria-hidden="true">闵</span>
      {showImage && !imageFailed ? (
        <Image
          alt="闵怡强头像"
          className={`absolute inset-0 object-cover transition-opacity duration-300 ${
            imageReady ? "opacity-100" : "opacity-0"
          }`}
          fill
          onError={() => setImageFailed(true)}
          onLoad={() => setImageReady(true)}
          priority
          sizes="(min-width: 640px) 10rem, 8rem"
          src="/profile/avatar.jpg"
        />
      ) : null}
    </div>
  );
}
