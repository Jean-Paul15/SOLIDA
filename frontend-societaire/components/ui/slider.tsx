"use client";

import * as React from "react";
import { Slider as SliderPrimitive } from "radix-ui";

import { cn } from "@/lib/utils";

function Slider({
  className,
  defaultValue,
  value,
  min = 0,
  max = 100,
  ...props
}: React.ComponentProps<typeof SliderPrimitive.Root>) {
  const valeurs = React.useMemo(
    () => (Array.isArray(value) ? value : Array.isArray(defaultValue) ? defaultValue : [min, max]),
    [value, defaultValue, min, max]
  );

  return (
    <SliderPrimitive.Root
      data-slot="slider"
      defaultValue={defaultValue}
      value={value}
      min={min}
      max={max}
      className={cn(
        "relative flex w-full touch-none items-center select-none py-3 data-disabled:opacity-50",
        className
      )}
      {...props}
    >
      <SliderPrimitive.Track className="relative h-2.5 w-full grow overflow-hidden rounded-full bg-neutre-200">
        <SliderPrimitive.Range className="absolute h-full bg-solida-teal-600" />
      </SliderPrimitive.Track>
      {valeurs.map((_, i) => (
        <SliderPrimitive.Thumb
          key={i}
          className="block size-7 shrink-0 rounded-full border-2 border-solida-teal-600 bg-blanc shadow-2 outline-none focus-visible:ring-4 focus-visible:ring-solida-teal-600/30"
        />
      ))}
    </SliderPrimitive.Root>
  );
}

export { Slider };
