# # **MIDI Playback Engine — Technical Review**
# 
# This is a good foundation for a MIDI playback engine. The overall architecture is sensible, particularly the separation from Qt, the use of absolute tick scheduling, precomputed tempo maps, and a single merged event timeline.
# 
# However, having examined the implementation, I think there are several areas worth addressing before treating it as a production-quality playback engine.
# 
# My overall assessment:
# 
# **Architecture**
# 
# Strong
# 
# The separation of transport, scheduling and UI responsibilities is correct.
# 
# **Timing and performance**
# 
# Needs improvement
# 
# The polling model and Python callback dispatch will limit timing precision.
# 
# **MIDI state management**
# 
# Important issues
# 
# Note ownership, controller chasing and shared-channel behaviour need attention.
# 
# **Feature completeness**
# 
# Room to expand
# 
# Several capabilities expected of a serious MIDI player are missing.
# 
# I would prioritise correctness of MIDI state management over micro-optimisation. There is little benefit in making the scheduler faster if it occasionally leaves notes hanging or restores the wrong instrument program.
# 
# # **1. What is already good**
# 
# There are several design decisions I would retain.
# 
# ### **1.1 Absolute tick scheduling**
# 
# Your approach of merging events from all MIDI tracks into one sorted event list is correct for synchronous MIDI Type 0 and Type 1 files.
# 
# ```
# self.events.sort(key=lambda e: e.absolute_tick)self._event_ticks = [e.absolute_tick for e in self.events]
# ```
# 
# Using `bisect` to locate the starting event is efficient:
# 
# ```
# def _find_start_index(self, start_tick: int) -> int:    return bisect.bisect_left(self._event_ticks, start_tick)
# ```
# 
# This is preferable to repeatedly iterating over individual tracks during playback.
# 
# **I would retain this design.**
# 
# In particular, I would not replace the event list with a priority queue or heap. A static, sorted timeline with a moving cursor is simpler and generally faster for this use case.
# 
# ### **1.2 Tempo map**
# 
# The segment-based tempo implementation is sensible.
# 
# You calculate cumulative time at every tempo change, allowing efficient conversion between ticks and seconds:
# 
# - `_build_time_map()`
# - `_tick_to_seconds()`
# - `seconds_to_tick()`
# - `_get_tempo_at_tick()`
# 
# This avoids having to recalculate the entire tempo history for every event.
# 
# It also supports tempo changes correctly in principle.
# 
# ### **1.3 Monotonic clock**
# 
# Using:
# 
# ```
# time.monotonic()
# ```
# 
# is the right decision.
# 
# Playback should not depend on system clock adjustments, daylight saving changes or changes to the computer's wall-clock time.
# 
# ### **1.4 Separation of responsibilities**
# 
# The engine does not depend on Qt, widgets or the MIDI player UI.
# 
# That is particularly important for your ElMo/JDXI Editor architecture.
# 
# The owner controls the engine, and the engine reports MIDI events through a callback.
# 
# This gives you flexibility to support:
# 
# - Hardware MIDI output.
# - Software synthesizers.
# - MIDI file rendering.
# - MIDI monitoring.
# - Playback visualisation.
# - Automated playback testing.
# 
# I would preserve that independence.
# 
# # **2. Important correctness issues**
# 
# These are the areas I would address first.
# 
# ## **2.1 Controller chasing is incomplete**
# 
# High priority
# 
# Your `_chase()` implementation finds the most recent controller value before the current playback position.
# 
# ```
# for event in self.events[: self.event_index]:    key = self._chase_key(event.message)    if key is not None and self._should_send(event):        target[key] = event
# ```
# 
# This works reasonably well when moving forwards through a file.
# 
# However, consider this sequence:
# 
# 1. At tick 1000, the instrument changes to Program 25.
# 2. At tick 2000, volume changes to 40.
# 3. At tick 3000, playback moves backwards to tick 500.
# 
# At tick 500, neither the program nor volume change has occurred.
# 
# Your `target` dictionary will not contain either value.
# 
# Consequently, `_chase()` has no reason to restore the previous program or volume.
# 
# The synthesizer can therefore retain values from the later playback position.
# 
# Your `_restore_defaults()` only handles a limited selection of known controller defaults. It does not provide a complete baseline for all chased state.
# 
# **Recommendation: introduce an explicit initial controller state.**
# 
# For each channel, maintain a baseline containing:
# 
# - Bank MSB and LSB.
# - Program.
# - Volume.
# - Expression.
# - Pan.
# - Modulation.
# - Sustain.
# - Pitch bend.
# - Other supported controllers.
# 
# When seeking, compare the desired state with the actual output state.
# 
# The desired state must include defaults for parameters that have not yet appeared in the file.
# 
# This is particularly important for backwards seeking.
# 
# Relevant implementation: `_chase()` and `_restore_defaults()`.&#x20;
# 
# Pasted markdown(20261115-213855).md
# 
# 
# 
# ## **2.2 Note tracking does not handle overlapping notes correctly**
# 
# High priority
# 
# Currently:
# 
# ```
# self._held_notes: dict[tuple[int, int], set[int]] = {}
# ```
# 
# The key is:
# 
# ```
# (channel, note)
# ```
# 
# and the value is a set of tracks.
# 
# This creates two problems.
# 
# **Problem A: repeated notes on the same track**
# 
# Imagine a track plays:
# 
# ```
# C4 ON
# C4 ON
# C4 OFF
# C4 OFF
# ```
# 
# The first note-off removes the track from the set entirely.
# 
# The engine no longer knows that another instance of C4 is outstanding.
# 
# You need a count, not a set.
# 
# For example:
# 
# ```
# held_notes: dict[    tuple[int, int],    dict[int, int]]
# ```
# 
# Where the nested dictionary represents:
# 
# ```
# (channel, note) -> {track_index: outstanding_note_count}
# ```
# 
# **Problem B: multiple tracks sharing a MIDI channel**
# 
# Suppose:
# 
# ```
# Track 1: C4 ON ---------------- C4 OFF
# Track 2:       C4 ON ---------------- C4 OFF
# ```
# 
# Both tracks use MIDI channel 1.
# 
# If Track 1 is muted, the engine sends a note-off for C4. However, MIDI note-off is channel-wide, not track-specific.
# 
# It can terminate Track 2's sounding C4 as well.
# 
# This is a fundamental limitation of trying to implement track-level note ownership on shared MIDI channels.
# 
# I would distinguish between:
# 
# - Logical note ownership within the playback engine.
# - Actual channel/note state at the MIDI destination.
# 
# You should also document that independent track muting is inherently limited when tracks share channels and play overlapping pitches.
# 
# ## **2.3 Sustain pedal ownership is similarly problematic**
# 
# Currently:
# 
# ```
# self._sustained_channels: dict[int, int] = {}
# ```
# 
# This assumes one track owns sustain for a given channel.
# 
# But sustain is a channel-wide controller.
# 
# If two tracks use the same channel and both issue sustain-on, muting one track can release sustain for the other.
# 
# I would replace this with channel-level effective sustain state and track-level ownership information.
# 
# The same underlying issue applies to other channel-wide controllers.
# 
# ## **2.4 Pause/resume can lose sustain state**
# 
# There is a specific issue here.
# 
# `pause()` calls:
# 
# ```
# self.release_held_notes()
# ```
# 
# This sends sustain-off.
# 
# However, `resume()` only chases controller state when:
# 
# ```
# if self._chase_pending:    self._chase()
# ```
# 
# `pause()` does not set `_chase_pending`.
# 
# Consequently, if sustain should be active at the paused position, resuming may leave it disabled.
# 
# I would explicitly restore controller state on resume, while deliberately not restoring notes that were sounding before the pause.
# 
# This distinction is important: controller state should be restored, but previously sounding notes should not spontaneously restart.
# 
# Pasted markdown(20261115-213855).md
# 
# ## **2.5 Reset and loading a new file can leave hanging notes**
# 
# Another lifecycle issue:
# 
# ```
# def reset(self):    ...    self._held_notes.clear()    self._sustained_channels.clear()
# ```
# 
# If the engine is playing when `reset()` is called, this discards the internal record of sounding notes without sending note-offs.
# 
# Similarly, `load_file()` calls `reset()`.
# 
# Therefore, loading another file during playback can leave notes sounding on the external synthesizer.
# 
# I would make reset perform an explicit release before clearing state, or require and enforce a stopped state.
# 
# Also consider what should happen when `start()` is called while already playing. It currently repositions the cursor without first releasing existing notes.
# 
# Pasted markdown(20261115-213855).md
# 
# ## **2.6 Controller restoration bypasses filtering**
# 
# There is a subtle issue in `_restore_defaults()`.
# 
# It uses:
# 
# ```
# self._send(msg)
# ```
# 
# rather than routing through the usual filtering and dispatch logic.
# 
# This means controller-reset messages can bypass:
# 
# - Track/channel mute rules.
# - Control-change suppression.
# 
# For example, a muted channel could still receive a controller reset when another channel is being restored.
# 
# I would centralise output filtering so that all outgoing MIDI messages follow the same policy, with an explicit exception mechanism for panic messages if necessary.
# 
# Pasted markdown(20261115-213855).md
# 
# # **3. Performance improvements**
# 
# The current engine is reasonably efficient during normal playback. Its main performance weakness is not the event list itself, but repeated work around seeking and event dispatch.
# 
# ## **3.1 Optimise controller chasing**
# 
# Most worthwhile optimisation
# 
# This is probably the first performance improvement I would implement.
# 
# Every chase currently scans all previous events:
# 
# ```
# for event in self.events[: self.event_index]:
# ```
# 
# This has two costs:
# 
# 1. O(N) traversal.
# 2. Creation of a potentially large list slice.
# 
# If the user repeatedly scrubs through a large MIDI file, this becomes unnecessary overhead.
# 
# ### **Suggested solution: controller-state snapshots**
# 
# Create periodic snapshots of controller state while building the event list.
# 
# For example:
# 
# ```
# @dataclass(frozen=True)class ControllerSnapshot:    event_index: int    channel_state: dict
# ```
# 
# Build a snapshot every 512 or 1024 events.
# 
# When seeking:
# 
# 1. Find the nearest preceding snapshot using binary search.
# 2. Restore its controller state.
# 3. Replay only events between the snapshot and target position.
# 4. Send the differences to the output device.
# 
# The resulting complexity becomes approximately:
# 
# \\[ O(\log N + K) \\]
# 
# Where K is the number of events since the last snapshot.
# 
# This is a substantial improvement for large MIDI files.
# 
# It also gives you a natural foundation for more sophisticated controller chasing.
# 
# ## **3.2 Cache time-signature ticks**
# 
# This method constructs a new list every time it is called:
# 
# ```
# idx = bisect.bisect_right(    [t for t, _, _ in self._time_signatures],    tick) - 1
# ```
# 
# Instead, maintain:
# 
# ```
# self._time_signature_ticks = [...]
# ```
# 
# when building the time-signature map.
# 
# This is a small improvement, but straightforward.
# 
# Pasted markdown(20261115-213855).md
# 
# ## **3.3 Reduce MIDI clock conversion overhead**
# 
# Currently:
# 
# ```
# def _next_clock_seconds(self):    return self._tick_to_seconds(self._next_clock_tick)
# ```
# 
# Every MIDI clock pulse involves a tempo-map lookup and tick-to-seconds conversion.
# 
# At 24 pulses per quarter note, that is 24 conversions per beat.
# 
# For ordinary playback this is not catastrophic, but it is unnecessary.
# 
# You could calculate the next clock deadline incrementally within the current tempo segment.
# 
# When a tempo boundary is crossed, recalculate using the new tempo.
# 
# This also makes clock scheduling easier to reason about.
# 
# There is another point worth checking: `_next_clock_tick` is initially zero, and `_send_song_position()` can align it exactly with the current playback position. This can cause an immediate clock pulse after Start or Continue. Verify that your first clock pulse and Song Position Pointer alignment follow the intended MIDI clock semantics.
# 
# ## **3.4 Avoid unnecessary message copying**
# 
# Your `_scaled()` method returns the original scheduled message when no velocity adjustment is needed:
# 
# ```
# if scale is None or msg.type != "note_on" or msg.velocity == 0:    return msg
# ```
# 
# This is efficient, but it exposes your internal event message to the callback.
# 
# If the output callback modifies the message, the scheduled event itself is modified.
# 
# I would make the internal scheduled representation immutable, or ensure the output adapter cannot mutate it.
# 
# For an optimised implementation, I would consider using immutable compiled event records and creating Mido messages only when dispatching.
# 
# ## **3.5 Instrument before micro-optimising**
# 
# I would add performance measurements for:
# 
# | Metric                      | Purpose                      |
# | --------------------------- | ---------------------------- |
# | Events per second           | Overall throughput           |
# | Maximum events per dispatch | Detect scheduling backlogs   |
# | Event lateness              | Measure timing accuracy      |
# | Chase duration              | Measure seek performance     |
# | Maximum dispatch latency    | Detect stalls                |
# | CPU usage                   | Identify processing overhead |
# 
# This will tell you whether the bottleneck is Python scheduling, MIDI message construction, the output callback or the actual MIDI device.
# 
# # **4. The biggest performance limitation: polling**
# 
# This is the architectural issue I would investigate most carefully.
# 
# Your documentation describes an external owner calling:
# 
# ```
# process_until_now()
# ```
# 
# every 5–20 ms.
# 
# That is convenient for integration with Qt, but it is not ideal for accurate MIDI playback.
# 
# Consider a MIDI file containing a rapid arpeggio.
# 
# At 120 BPM and 480 PPQ:
# 
# \\[ 1\text{ tick} = 1.042\text{ ms} \\]
# 
# A 10 ms timer interval corresponds to approximately 9.6 ticks.
# 
# Several events can therefore become due between polling calls.
# 
# Your `_send_due()` method will send all overdue events in sequence, but they will be delivered to the output device in a burst rather than at their intended times.
# 
# This is especially relevant to the complex arpeggiated sequences you have been working with.
# 
# ### **My recommendation: introduce a dedicated playback scheduler**
# 
# I would retain the current engine API but give the playback owner a more sophisticated scheduling mechanism.
# 
# **Proposed playback architecture**
# 
# **PlaybackEngine**
# 
# Transport, position, loops, tempo, mute, chase
# 
# **PlaybackScheduler**
# 
# High-resolution deadlines and event dispatch
# 
# **MIDI Output**
# 
# Timestamped hardware events
# 
# **Software Synth**
# 
# Synthesizer event queue
# 
# The scheduler should ideally:
# 
# - Run independently of the Qt UI thread.
# - Wait for the next event deadline rather than polling at a fixed interval.
# - Dispatch events as close as possible to their scheduled times.
# - Use timestamped MIDI output where the backend supports it.
# - Support cancellation and rescheduling on seek, pause and stop.
# 
# Python cannot provide hard real-time guarantees, but this architecture should improve timing substantially.
# 
# I would not put thread management inside `PlaybackEngine` itself. Keep the engine deterministic and let the playback owner manage scheduling.
# 
# # **5. Missing MIDI playback features**
# 
# The engine already implements a reasonable subset of playback functionality.
# 
# However, I would consider the following additions.
# 
# ## **5.1 Track and channel controls**
# 
# | Feature                | Priority | Comments                                |
# | ---------------------- | -------- | --------------------------------------- |
# | Track mute             | Existing | Needs note-ownership improvements       |
# | Channel mute           | Existing | Needs shared-channel handling           |
# | Track solo             | High     | Essential for MIDI editing              |
# | Multiple-track solo    | High     | Support solo groups                     |
# | Track transpose        | High     | Useful for experimentation              |
# | Track velocity scaling | Existing | Consider zero-scale semantics           |
# | Track volume           | High     | Independent of note velocity            |
# | Track pan              | Medium   | Useful for arranging                    |
# | Channel remapping      | High     | Particularly useful for hardware synths |
# | Note range filtering   | Medium   | Useful for isolating parts              |
# 
# One specific issue: `set_track_velocity_scale(0.0)` currently produces velocity 1 because `_scaled()` enforces a minimum velocity of 1.
# 
# If zero means silence, it should suppress the note-on rather than turn it into a very quiet note.
# 
# ## **5.2 More complete controller support**
# 
# Your current controller chase handles:
# 
# - Program changes.
# - Pitch bend.
# - Most control changes.
# 
# However, there are other important MIDI messages to consider.
# 
# | MIDI message           | Suggested support                       |
# | ---------------------- | --------------------------------------- |
# | Channel pressure       | Chase                                   |
# | Polyphonic aftertouch  | Note-specific state                     |
# | Bank select            | Existing, improve restoration           |
# | RPN                    | Stateful ordered restoration            |
# | NRPN                   | Stateful ordered restoration            |
# | Data Entry MSB/LSB     | RPN/NRPN integration                    |
# | Pitch bend sensitivity | RPN support                             |
# | Channel mode messages  | Explicit handling                       |
# | SysEx                  | Pass-through policy and device handling |
# 
# An important detail: RPN and NRPN messages cannot safely be treated as independent controller values.
# 
# For example, CC 101/100 selects an RPN, while CC 6/38 supplies data.
# 
# Your current `_chase()` sorts controller keys numerically before dispatching them. That can destroy the ordering needed to reconstruct RPN/NRPN state.
# 
# I would introduce a dedicated stateful controller representation that understands these message sequences.
# 
# ## **5.3 Transport features**
# 
# Some useful additions:
# 
# - Quantised seeking to the nearest beat/bar.
# - Count-in.
# - Metronome.
# - Loop count.
# - Legato looping.
# - Configurable loop-boundary behaviour.
# - Tempo tap.
# - Tempo multiplier.
# - MIDI clock synchronisation.
# - MIDI Start/Continue/Stop.
# - Song Position Pointer.
# - MIDI Time Code support, if synchronisation with external equipment is required.
# 
# You already have several of the more sophisticated transport features, including A–B looping, playback speed and MIDI clock.
# 
# One loop issue worth correcting: `_wrap_loop()` resets overshoot to zero when the playback delay exceeds the loop duration. A sufficiently long scheduler stall can therefore lose elapsed playback time and fail to process multiple loop iterations correctly.
# 
# The loop implementation should handle multiple crossed boundaries explicitly.
# 
# Pasted markdown(20261115-213855).md
# 
# # **6. MIDI file format considerations**
# 
# One important limitation is that your implementation assumes a global timeline.
# 
# That is appropriate for:
# 
# - MIDI Type 0.
# - MIDI Type 1.
# 
# However, MIDI Type 2 contains independent sequences. Merging these tracks into a single timeline is not generally valid.
# 
# I would explicitly validate the file type in `load_file()` and either reject Type 2 or implement separate sequence playback.
# 
# I would also define deterministic behaviour for conflicting tempo and time-signature events occurring at the same tick in different tracks.
# 
# # **7. Recommended architectural improvements**
# 
# I would consider separating the current implementation into four logical components.
# 
# This does not necessarily mean four separate Python modules immediately.
# 
# **1. MidiTimeline**
# 
# Static data
# 
# - Merged, sorted MIDI events.
# - Absolute tick positions.
# - Tempo and time-signature maps.
# - Tick/seconds conversion.
# - Track and channel indexes.
# - Controller-state checkpoints.
# 
# **2. PlaybackTransport**
# 
# Transport state
# 
# - Start, stop, pause, resume.
# - Seek and scrub.
# - Playback speed.
# - A–B loops.
# - Position tracking.
# 
# **3. MidiPlaybackState**
# 
# Stateful MIDI logic
# 
# - Active notes.
# - Note ownership.
# - Sustain.
# - Controller state.
# - Program and bank state.
# - Mute, solo and chase.
# 
# **4. MidiOutput**
# 
# Output abstraction
# 
# - Hardware MIDI.
# - Software synthesizers.
# - Timestamped output.
# - Message filtering.
# - Panic and recovery.
# - Device errors and reconnection.
# 
# The key distinction is between the immutable musical timeline and the mutable state of the playback destination.
# 
# That distinction becomes increasingly important when you support seeking, looping, multiple outputs and live MIDI control.
# 
# I would also consider defining an output protocol:
# 
# ```
# class MidiOutput(Protocol):    def send(self, message: mido.Message) -> None:        ...    def send_batch(        self,        messages: Sequence[mido.Message]    ) -> None:        ...    def panic(self) -> None:        ...
# ```
# 
# The batch operation is optional, but it provides an opportunity to optimise output dispatch without coupling the engine to a particular MIDI backend.
# 
# # **8. Testing I would introduce**
# 
# I would place considerable emphasis on automated testing because transport and controller bugs are often difficult to reproduce manually.
# 
# These are the tests I would prioritise.
# 
# | Test                             | Expected behaviour                    |
# | -------------------------------- | ------------------------------------- |
# | Variable tempo                   | Correct absolute event times          |
# | Simultaneous events              | Deterministic ordering                |
# | Seek forwards                    | Correct controller state              |
# | Seek backwards                   | No stale controller values            |
# | Seek before first program change | Correct initial program state         |
# | Pause/resume with sustain        | Sustain correctly restored            |
# | Repeated identical notes         | Correct note ownership                |
# | Two tracks sharing a channel     | No unintended note termination        |
# | Mute during active note          | Correct note release                  |
# | Unmute during playback           | Correct controller restoration        |
# | Loop across tempo change         | Correct timing                        |
# | Long scheduler stall during loop | Correct loop recovery                 |
# | Load new file during playback    | No hanging notes                      |
# | MIDI clock                       | Correct pulse frequency and alignment |
# | Type 2 MIDI file                 | Explicit handling                     |
# 
# I would also introduce a fake MIDI output that records messages and their dispatch timestamps. This allows most of the engine to be tested without any hardware.
# 
# # **9. My prioritised implementation roadmap**
# 
# I would approach this incrementally rather than attempting a major rewrite.
# 
# **Phase 1 — Correctness**
# 
# Do first
# 
# 1. Fix controller chasing and initial-state restoration.
# 2. Fix overlapping note tracking.
# 3. Address shared-channel note and sustain ownership.
# 4. Fix pause/resume controller restoration.
# 5. Fix reset/load/start lifecycle behaviour.
# 6. Ensure controller restoration respects mute and suppression.
# 
# **Phase 2 — Performance**
# 
# Next
# 
# 1. Implement controller-state snapshots.
# 2. Cache time-signature indexes.
# 3. Optimise MIDI clock timing.
# 4. Introduce a dedicated scheduler.
# 5. Benchmark dense MIDI playback.
# 
# **Phase 3 — Functionality**
# 
# Expansion
# 
# 1. Track solo.
# 2. Track transpose.
# 3. Channel remapping.
# 4. RPN/NRPN support.
# 5. More comprehensive controller chasing.
# 6. Improved loop and synchronisation functionality.
# 
# **Phase 4 — Integration**
# 
# Production
# 
# 1. Hardware MIDI output abstraction.
# 2. Software synthesizer integration.
# 3. Timestamped MIDI scheduling.
# 4. Output latency measurement.
# 5. Recovery from MIDI device errors.
# 
# # **10. Final assessment**
# 
# I would not rewrite this engine. Its core design is good, and the sorted event list, tempo mapping and transport separation are worth preserving.
# 
# However, I would make three substantial changes:
# 
# **First: make MIDI state management much more sophisticated.**
# 
# This is the most important issue. Note ownership, controller restoration and shared-channel behaviour need to be reliable.
# 
# **Second: introduce controller-state snapshots.**
# 
# This improves seeking performance and gives you a much better foundation for controller chasing.
# 
# **Third: separate scheduling from the transport engine.**
# 
# The current polling approach is perfectly reasonable for a first implementation, but a dedicated scheduler and timestamped MIDI output would be a significant improvement for accurate playback.
# 
# For ElMo/JDXI Editor, I would particularly prioritise accurate playback of dense, complex arpeggiated MIDI sequences. That requires reliable event timing, overlapping-note handling, controller restoration and predictable hardware output.
# 
# **My recommendation:** retain `PlaybackEngine` as the high-level transport API, but evolve its internals into a proper timeline, playback-state and output architecture.
# 
# I can take the next step by producing a concrete refactoring specification, including revised dataclasses, method signatures and unit tests for the five most important correctness problems.
# 
# 🎹Review revised MIDI playback engineTap to set up

I would approach this as a **targeted refactoring of the existing MIDI playback engine**, preserving its public API wherever possible while correcting the underlying state-management and scheduling issues.

The objective is to make it reliable enough for professional MIDI playback, particularly with dense arpeggios, overlapping notes, multiple tracks sharing channels, and external hardware such as the Roland JD-Xi.

Below is the proposed implementation specification. It includes the revised architecture, dataclasses, method signatures, behavioural contracts and unit-test plan.

# **1. Target architecture**

I recommend separating the engine into four cooperating components.

**PlaybackEngine**

Public API — backward-compatible transport facade

**MidiTimeline**

Events, tempo maps, indexes and snapshots

**PlaybackTransport**

Position, state, loops and speed

**MidiPlaybackState**

Notes, controllers, mute, solo and chase

**MidiScheduler**

Deadlines, dispatch and clock

**MidiOutput Protocol**

Hardware MIDI / FluidSynth / other software synthesizers

The important architectural principle is that the timeline is immutable after compilation, whereas playback state is mutable.

The scheduler should not own musical state, and the MIDI output should not know anything about tracks, loops or transport position.

# **2. Revised data structures**

I would introduce the following dataclasses.

## **2.1 ScheduledEvent**

Retain the existing concept, but provide deterministic ordering.

```
@dataclass(frozen=True, slots=True)class ScheduledEvent:    absolute_tick: int    track_index: int    sequence_index: int    message: mido.Message
```

`sequence_index` preserves the original order of messages within a track.

This is important when multiple events share the same tick, particularly:

- Note-off followed by note-on.
- Bank select followed by program change.
- RPN selection followed by Data Entry.
- Simultaneous events from multiple tracks.

Sort by:

```
(absolute_tick, track_index, sequence_index)
```

This gives deterministic ordering, although the cross-track ordering policy should be documented because MIDI files do not define a universal ordering for simultaneous events across tracks.

## **2.2 ControllerState**

This is probably the most important new abstraction.

```
@dataclassclass ChannelControllerState:    bank_msb: int = 0    bank_lsb: int = 0    program: int = 0    volume: int = 100    expression: int = 127    pan: int = 64    modulation: int = 0    sustain: int = 0    pitch_bend: int = 0    channel_pressure: int = 0    controllers: dict[int, int] = field(        default_factory=dict    )    rpn_msb: int = 127    rpn_lsb: int = 127    nrpn_msb: int = 127    nrpn_lsb: int = 127    data_entry_msb: int = 0    data_entry_lsb: int = 0
```

A distinction is necessary here: these values define a playback-state model, not universal synthesizer defaults.

In particular, the actual initial state of an external MIDI device is not necessarily known. The engine should support a configurable initial-state policy rather than assume that every synthesizer has the same defaults.

The state object should provide:

```
def apply(self, message: mido.Message) -> None:    ...def diff(self, other: "ChannelControllerState") -> list[mido.Message]:    ...
```

For RPN and NRPN, restoration must generate correctly ordered message sequences rather than treating every CC independently.

## **2.3 ActiveNote**

Replace the current track set with explicit note accounting.

```
@dataclassclass ActiveNote:    channel: int    note: int    track_index: int    velocity: int    count: int = 1
```

The state manager maintains:

```
active_notes: dict[    tuple[int, int, int],    ActiveNote]
```

The key is:

```
(track_index, channel, note)
```

This allows repeated note-ons on the same track to be counted independently.

Also maintain channel-level aggregate counts:

```
channel_note_counts: dict[    tuple[int, int],    int]
```

**Important MIDI limitation:** MIDI 1.0 note-off messages identify a channel and pitch, not a track or individual note instance. Therefore, overlapping identical pitches from different tracks sharing a channel cannot always be independently muted. The engine needs an explicit policy: defer note release, mute the whole channel, or isolate tracks onto separate channels.

I recommend supporting channel remapping as the most useful solution for independent track control.

## **2.4 ControllerSnapshot**

```
@dataclass(frozen=True)class ControllerSnapshot:    event_index: int    tick: int    channels: dict[        int, ChannelControllerState    ]
```

Snapshots are generated during timeline compilation.

Initial interval: 512 events.

This should be configurable and benchmarked rather than treated as a fixed optimal value.

# **3. Revised method responsibilities**

The existing `PlaybackEngine` should remain the public entry point.

I would preserve the majority of its existing methods.

| Existing method        | Proposed responsibility                       |
| ---------------------- | --------------------------------------------- |
| `load_file()`          | Compile and install a timeline                |
| `start()`              | Start transport and restore destination state |
| `stop()`               | Stop, release notes and terminate clock       |
| `pause()`              | Freeze position and release sounding notes    |
| `resume()`             | Restore controller state and continue         |
| `seek_tick()`          | Reposition, release notes and chase state     |
| `seek_seconds()`       | Convert seconds and delegate                  |
| `process_until_now()`  | Process due events                            |
| `set_speed()`          | Change playback rate                          |
| `set_loop()`           | Configure loop boundaries                     |
| `_chase()`             | Delegate to state manager                     |
| `_dispatch()`          | Delegate filtering and output                 |
| `release_held_notes()` | Delegate to state manager                     |
| `all_notes_off()`      | Invoke output recovery/panic                  |

The key change is that `PlaybackEngine` becomes an orchestrator rather than the owner of every internal implementation detail.

# **4. Critical behavioural contracts**

I would formalise the following behaviours before changing the implementation.

## **4.1 Seeking**

Seeking must be transactional.

The sequence should be:

1. Calculate the target tick.
2. Release notes currently sounding.
3. Stop MIDI clock temporarily if required.
4. Locate the nearest controller snapshot.
5. Reconstruct controller state up to the target.
6. Restore the output device to the desired state.
7. Position the event cursor.
8. Re-establish the transport clock.
9. Resume dispatch if playback was active.

An important distinction:

- Seeking must restore controllers.
- Seeking must not replay historical note-ons.
- Seeking must not restore previously sounding notes.
- Events exactly at the target tick should remain eligible for dispatch.

I would retain `bisect_left()` for locating the event cursor, so events at the target tick are included.

## **4.2 Pause and resume**

Define the behaviour explicitly:

| Operation | Notes                              | Controllers                                 | Transport  |
| --------- | ---------------------------------- | ------------------------------------------- | ---------- |
| Pause     | Release                            | Preserve desired state                      | Freeze     |
| Resume    | Do not restart old notes           | Restore                                     | Continue   |
| Stop      | Release                            | Mark destination state for reinitialisation | Stop       |
| Seek      | Release                            | Chase target state                          | Reposition |
| Loop      | Release or apply configured policy | Chase loop-start state                      | Continue   |

One subtlety: after pause, the engine's logical controller state should remain intact even if it has temporarily sent sustain-off to the destination.

This is why logical state and output state should be tracked separately.

## **4.3 Output-state tracking**

Introduce two separate concepts:

```
desired_state: ChannelStateMapoutput_state: ChannelStateMap
```

`desired_state` describes what the MIDI file says should be active.

`output_state` describes what the engine believes it has actually sent.

The distinction solves several problems:

- Mute can change desired state without pretending the device received it.
- Suppression can prevent messages without corrupting logical state.
- Seeking can calculate the correct output differences.
- Device reconnection can invalidate output state and trigger reinitialisation.

A further improvement would be an `output_state_valid` flag, invalidated after a device error or external MIDI intervention.

# **5. Revised API signatures**

I would keep the existing public methods but introduce a few additional ones.

```
class PlaybackEngine:    # File and timeline    def load_file(self, midi_file: mido.MidiFile) -> None: ...    # Transport    def start(self, start_tick: int = 0) -> None: ...    def stop(self) -> None: ...    def pause(self) -> None: ...    def resume(self) -> None: ...    def seek_tick(self, tick: int) -> None: ...    def seek_seconds(self, seconds: float) -> None: ...    # Playback controls    def set_speed(self, speed: float) -> None: ...    def set_loop(        self,        enabled: bool,        loop_range: tuple[int, int] | None = None,    ) -> None: ...    # Track controls    def mute_track(self, track_index: int, muted: bool) -> None: ...    def solo_track(self, track_index: int, solo: bool) -> None: ...    def set_track_velocity_scale(        self, track_index: int, scale: float    ) -> None: ...    def set_track_transpose(        self, track_index: int, semitones: int    ) -> None: ...    def set_track_channel(        self, track_index: int, channel: int    ) -> None: ...    # Channel controls    def mute_channel(self, channel: int, muted: bool) -> None: ...    def all_notes_off(self) -> None: ...    # Scheduler integration    def process_until_now(self) -> bool: ...    def next_deadline(self) -> float | None: ...    # Output    def set_output(self, output: MidiOutput) -> None: ...
```

`next_deadline()` is particularly useful.

It allows an external scheduler to determine when the next event should be dispatched, instead of waking up at arbitrary fixed intervals.

I would also introduce an event notification mechanism for the UI, separate from the actual MIDI output callback. For example, the track viewer should be able to receive playback-position and active-note updates without being coupled to hardware dispatch.

# **6. Scheduler design**

I would keep the existing polling implementation as a compatibility mode.

However, introduce a scheduler interface:

```
class MidiScheduler(Protocol):    def start(self) -> None: ...    def stop(self) -> None: ...    def wake(self) -> None: ...    def schedule_changed(self) -> None: ...
```

Two implementations would be useful:

| Scheduler           | Intended use                       |
| ------------------- | ---------------------------------- |
| `PollingScheduler`  | Qt integration and simple playback |
| `DeadlineScheduler` | High-precision background playback |

The deadline scheduler should:

1. Read the next event deadline.
2. Wait until close to that deadline.
3. Process all due events.
4. Calculate the next deadline.
5. Repeat.

For hardware output, use backend-supported timestamp scheduling where available. A background Python thread alone does not guarantee accurate MIDI timing.

I would avoid a busy-wait loop. It wastes CPU and still does not provide hard real-time guarantees.

Also, do not let a scheduler call Qt widgets directly. UI notifications should be marshalled through Qt signals or an equivalent thread-safe mechanism.

# **7. Five essential correctness test suites**

I would make these the acceptance criteria for Phase 1.

## **Test 1 — Controller chasing in both directions**

Create a MIDI file containing:

```
Tick 0:    Program Change 1
Tick 100:  Volume 100
Tick 200:  Program Change 25
Tick 300:  Volume 40
```

Test:

- Start at tick 250: program 25, volume 100.
- Seek to tick 150: program 1, volume 100.
- Seek to tick 350: program 25, volume 40.
- Seek to tick 50: program 1 and the configured initial volume.

The final test is particularly important because it exposes stale controller values.

## **Test 2 — Overlapping notes**

Create:

```
Track 1:
Tick 0:   C4 ON
Tick 100: C4 ON
Tick 200: C4 OFF
Tick 300: C4 OFF
```

Expected internal note counts:

| Tick | Active count |
| ---- | ------------ |
| 0    | 1            |
| 100  | 2            |
| 200  | 1            |
| 300  | 0            |

Muting and stopping must leave the internal note registry empty.

Also test two tracks sharing the same channel and pitch. Verify the selected shared-channel policy explicitly.

## **Test 3 — Pause/resume and sustain**

Create:

```
Tick 0:   Sustain ON
Tick 100: C4 ON
Tick 200: Pause
Tick 200: Resume
Tick 300: C4 OFF
Tick 400: Sustain OFF
```

Expected:

- Pause releases the sounding note.
- Pause sends sustain-off to prevent stuck notes.
- Resume restores sustain-on.
- Resume does not restart C4.
- The subsequent note-off does not create an inconsistent note state.

## **Test 4 — File replacement and lifecycle**

Test these sequences:

```
Load A → Start → Load B
Load A → Start → Reset
Load A → Start → Start at tick 500
Load A → Start → Stop → Start
```

Verify that:

- All sounding notes are released.
- Sustain is released.
- The event cursor is valid.
- No stale controller state is retained.
- The new file starts at the requested position.

## **Test 5 — Muting and controller suppression**

Create two tracks sharing a channel.

Track 1 contains program changes, volume and notes.

Track 2 contains notes and sustain changes.

Test:

- Muting Track 1.
- Unmuting Track 1.
- Muting the channel.
- Suppressing program changes.
- Suppressing control changes.

Verify that logical controller state and actual output state remain consistent.

# **8. Additional test and benchmark infrastructure**

I would introduce a reusable recording output.

```
@dataclassclass RecordedMessage:    timestamp: float    message: mido.Messageclass RecordingMidiOutput:    def __init__(self):        self.messages: list[RecordedMessage] = []    def send(self, message: mido.Message) -> None:        self.messages.append(            RecordedMessage(                timestamp=time.monotonic(),                message=message.copy(),            )        )    def clear(self) -> None:        self.messages.clear()
```

This allows deterministic functional tests and integration tests without connecting the JD-Xi.

For timing benchmarks, I would additionally inject a fake clock rather than depend on `time.monotonic()`.

Suggested benchmark files:

| MIDI file                | Purpose               |
| ------------------------ | --------------------- |
| 4-track, 1-minute file   | Basic playback        |
| 16-track, 5-minute file  | Normal complexity     |
| 32-track, 10-minute file | Larger project        |
| 100,000 events           | Dense event dispatch  |
| 1 million events         | Timeline scalability  |
| Dense arpeggio sequence  | Timing stress test    |
| Multiple tempo changes   | Tempo-map correctness |

Measure event lateness, maximum dispatch duration, CPU utilisation and controller-chase latency.

# **9. Implementation order and migration strategy**

I would deliberately avoid implementing everything at once.

| Step | Change                                    | Risk   |
| ---- | ----------------------------------------- | ------ |
| 1    | Introduce `ChannelControllerState`        | Low    |
| 2    | Introduce separate desired/output state   | Medium |
| 3    | Replace held-note sets with note counts   | Medium |
| 4    | Correct pause/resume and reset lifecycle  | Medium |
| 5    | Introduce controller snapshots            | Medium |
| 6    | Extract `MidiTimeline`                    | Medium |
| 7    | Extract `MidiPlaybackState`               | Medium |
| 8    | Introduce `MidiOutput` protocol           | Low    |
| 9    | Add deadline scheduler                    | Higher |
| 10   | Add solo, transpose and channel remapping | Medium |

**Maintain backward compatibility wherever possible.**

In particular, existing JDXI Editor code should continue to be able to use:

```
engine.start()engine.pause()engine.resume()engine.stop()engine.seek_tick(960)engine.process_until_now()
```

I would also retain `on_event` during the migration, implementing it as an adapter to the new output interface.

# **10. Architectural decisions I would settle now**

There are five decisions that will influence the longer-term design.

| Decision              | Recommendation                                           |
| --------------------- | -------------------------------------------------------- |
| Event representation  | Immutable compiled timeline                              |
| Timing representation | Absolute ticks plus tempo-aware seconds                  |
| Controller state      | Separate desired and output states                       |
| Note ownership        | Track-level counts plus channel-level aggregation        |
| Threading             | Scheduler owned externally, never by the transport model |

One further recommendation: keep the engine MIDI 1.0 compatible initially, but design the output abstraction so that MIDI 2.0 support can be added later without rewriting the transport.

This is particularly worthwhile if you eventually want to support richer controller resolution and per-note expression.

# **My recommendation for the actual refactoring**

Recommended approach

I would start with the existing `PlaybackEngine` rather than immediately splitting it into multiple files.

First introduce the new state objects and fix the five correctness problems. Once the tests pass, extract the responsibilities into separate modules.

A possible final package structure:

```
elmo/
└── midi/
    └── playback/
        ├── __init__.py
        ├── engine.py
        ├── timeline.py
        ├── transport.py
        ├── scheduler.py
        ├── playback_state.py
        ├── controller_state.py
        ├── note_state.py
        ├── output.py
        ├── events.py
        └── tests/
            ├── test_timeline.py
            ├── test_transport.py
            ├── test_controller_state.py
            ├── test_note_state.py
            ├── test_seeking.py
            ├── test_looping.py
            └── test_scheduler.py
```

I would not create separate abstractions for every small operation. The objective is clear ownership of responsibilities, not maximum class count.

**The most important design change is separating MIDI playback state from transport state.** That will make the engine considerably easier to extend, test and optimise.

The next logical step is to implement Phase 1 against your actual `PlaybackEngine` source, preserving existing callers and providing regression tests for the five correctness problems.

Would you like me to work through that implementation as a minimal, testable patch?

🎹Review Phase 1 MIDI implementationTap to set up