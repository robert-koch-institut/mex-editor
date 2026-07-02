import { parse } from "@typescript-eslint/typescript-estree";

function isProbablyCode(text) {
  const trimmed = text.trim();
  if (!trimmed) return false;

  // some directives/annotation to execlude
  if (/^(eslint-disable|eslint-enable|prettier-ignore|@ts-|TODO|FIXME|NOTE|HACK)/i.test(trimmed)) {
    return false;
  }

  try {
    const ast = parse(trimmed, { errorOnUnknownASTType: false, loc: false, range: false });
    return ast.body.length > 0;
  } catch {
    // Unable to pase to code -> normal comment
    return false;
  }
}

export default {
  meta: {
    type: "suggestion",
    docs: { description: "Disallow comments that contain commented-out code" },
    schema: [],
    messages: {
      commentedOutCode: "This Comment looks like code. Please remove.",
    },
  },
  create(context) {
    return {
      Program() {
        const sourceCode = context.sourceCode ?? context.getSourceCode();
        for (const comment of sourceCode.getAllComments()) {
          if (isProbablyCode(comment.value)) {
            context.report({ loc: comment.loc, messageId: "commentedOutCode" });
          }
        }
      },
    };
  },
};
