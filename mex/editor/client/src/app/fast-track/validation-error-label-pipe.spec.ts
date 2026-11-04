import { ValidationErrorMessagePipe } from "./validation-error-label-pipe";

describe("ValidationErrorLabelPipe", () => {
  it("create an instance", () => {
    const pipe = new ValidationErrorMessagePipe();
    expect(pipe).toBeTruthy();
  });
});
