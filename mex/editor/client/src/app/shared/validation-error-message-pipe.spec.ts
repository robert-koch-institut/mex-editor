import { ValidationErrorMessagePipe } from "./validation-error-message-pipe";

describe("ValidationErrorLabelPipe", () => {
  it("create an instance", () => {
    const pipe = new ValidationErrorMessagePipe();
    expect(pipe).toBeTruthy();
  });
});
