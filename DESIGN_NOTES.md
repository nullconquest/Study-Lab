# Study Lab experimental interface

## Direction

The interface treats Study Lab as a working machine, not a decorative science-fiction poster.
It borrows the layered information hierarchy of cinematic holographic engineering desks and
the clarity of industrial control rooms: cyan means a live system, amber means an operation or
attention state, and green is reserved for confirmed readiness.

The app does not use a copyrighted film still as a background or pretend that random numbers are
live telemetry. Its readouts describe real application state: whether the local core is running,
whether an API key is present, whether a set or guide is active, and how much real work is saved.

## Interaction principles

- The circular core moves subtly so the machine feels powered without distracting from study.
- Every workspace receives its own literal module code and purpose label.
- The Core Chamber replaces sidebar navigation: six native button entrances surround a central reactor with circuit branches. Every module offers Return to Core.
- Create Questions, Create Study Guide, Study, Rapid Fire, Coverage & Edit and Archives open existing workspaces. Question and guide archives have direct switching controls; active guides can be opened from the Core.
- Reduced-motion preferences disable the ambient animations.
- The visual layer lives in `forge/ui.py`; it can be replaced independently of learning logic.

## Reference categories

- Tony Stark-style transparent engineering workstations: layered panes, central focus and warm/cool contrast.
- Modern industrial HMI/control rooms: status colors, dense but readable modules and continuous-system presence.
- Digital-twin dashboards: restrained grids, fine-line geometry and bounded data panels.

## Core Chamber revision — October 9, 2026

The core is CSS geometry, with counter-rotating cyan rings and an amber ring.
Native Streamlit buttons provide keyboard-accessible routing without HTML link hacks.
Module navigation changes only lab_page and preserves loaded work, answer history,
Rapid Fire progress and study position. API configuration reports only key presence;
it does not imply that a remote connection has been verified.

At narrow widths, module cards and the reactor stack. All ambient motion honors
prefers-reduced-motion. Automated Streamlit execution was tested; visual browser
QA and live API requests were not performed in this environment.
