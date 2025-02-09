import { useEffect, useState } from "react";

interface PixelatedTextProps {
  text: string;
  interval?: number;
}

export const PixelatedText = ({ text, interval = 50 }: PixelatedTextProps) => {
  const [displayText, setDisplayText] = useState("");
  const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()";

  useEffect(() => {
    let currentIndex = 0;
    let intervalId: NodeJS.Timeout;

    const animateText = () => {
      intervalId = setInterval(() => {
        setDisplayText((prevText) => {
          const textArray = prevText.split("");
          if (currentIndex < text.length) {
            textArray[currentIndex] = characters[Math.floor(Math.random() * characters.length)];
            return textArray.join("");
          }
          return prevText;
        });
      }, interval / 4);

      setTimeout(() => {
        clearInterval(intervalId);
        setDisplayText(text.substring(0, currentIndex + 1));
        currentIndex++;

        if (currentIndex < text.length) {
          animateText();
        }
      }, interval);
    };

    setDisplayText("");
    currentIndex = 0;
    animateText();

    return () => clearInterval(intervalId);
  }, [text, interval]);

  return <span className="font-mono">{displayText}</span>;
};
