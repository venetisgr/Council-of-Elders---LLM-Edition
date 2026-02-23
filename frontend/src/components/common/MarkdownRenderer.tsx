import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({
  content,
  className = "",
}: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      className={`prose prose-sm max-w-none
        prose-headings:font-display prose-headings:text-ink
        prose-p:text-ink/90 prose-p:leading-relaxed
        prose-a:text-ocean prose-a:no-underline hover:prose-a:underline
        prose-strong:text-ink
        prose-code:text-bronze prose-code:bg-sand/50 prose-code:px-1 prose-code:rounded
        prose-pre:bg-night prose-pre:rounded-lg
        prose-ul:text-ink/90 prose-ol:text-ink/90
        prose-blockquote:border-bronze/50 prose-blockquote:text-stone
        ${className}
      `}
      remarkPlugins={[remarkGfm]}
      components={{
        code({ className: codeClassName, children, ...props }) {
          const match = /language-(\w+)/.exec(codeClassName || "");
          const codeString = String(children).replace(/\n$/, "");

          if (match) {
            return (
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
              >
                {codeString}
              </SyntaxHighlighter>
            );
          }

          return (
            <code className={codeClassName} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
