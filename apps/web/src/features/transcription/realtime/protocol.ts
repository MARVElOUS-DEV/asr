export type ClientStartEvent = {
  type: "start";
  session_id?: string;
  sample_rate: number;
  language: string;
};

export type ClientStopEvent = {
  type: "stop";
};

export type ClientEvent = ClientStartEvent | ClientStopEvent;

export type ServerReadyEvent = {
  type: "ready";
  session_id: string;
};

export type ServerPartialEvent = {
  type: "partial";
  session_id: string;
  text: string;
};

export type ServerFinalEvent = {
  type: "final";
  session_id: string;
  text: string;
};

export type ServerErrorEvent = {
  type: "error";
  message: string;
};

export type ServerEvent =
  | ServerReadyEvent
  | ServerPartialEvent
  | ServerFinalEvent
  | ServerErrorEvent;
