import Darwin
import Foundation
import os

/// Watches the main thread from a background queue, on macOS 13 and later: its share of the CPU (the kernel's own accounting of the thread, as `sample` sees it) and how late a block posted to it every 8 ms ran (a stall: frames not drawn).
///
/// Call `MainThreadMeter.shared.start()` once on the main thread, then `read()` from one thread at any interval, for example twice a second from a timer, to get what happened since the last reading. `beginEpisode()` and `endEpisode()` time one action, such as a tab switch, apart from the readings.
public final class MainThreadMeter: @unchecked Sendable {
    public struct Reading: Sendable {
        /// The main thread's share of wall time on the CPU, 0 to 100.
        public var busy: Double
        /// The longest a posted block waited, in milliseconds.
        public var worstStall: Double
        /// Blocks that waited longer than a 60 Hz frame (16.7 ms).
        public var lateFrames: Int
    }

    public static let shared = MainThreadMeter()

    private let queue = DispatchQueue(label: "main-thread-meter", qos: .userInteractive)
    private let stalls = OSAllocatedUnfairLock(initialState: (worst: 0.0, late: 0))
    private let episode = OSAllocatedUnfairLock(initialState: 0.0)
    private var mainThread: thread_act_t = 0
    private var lastCPU: Double = 0
    private var lastWall: Double = 0
    private var pinger: DispatchSourceTimer?

    /// Starts watching. Call it on the main thread, which it records.
    @MainActor public func start() {
        guard pinger == nil else { return }
        mainThread = mach_thread_self()
        lastCPU = cpuTime()
        lastWall = Self.now()
        pinger = makePinger()
    }

    /// What happened since the last reading.
    public func read() -> Reading {
        let cpu = cpuTime(), wall = Self.now()
        let busy = wall > lastWall ? min(100, max(0, (cpu - lastCPU) / (wall - lastWall) * 100)) : 0
        lastCPU = cpu
        lastWall = wall
        let (worst, late) = stalls.withLock { value in
            defer { value = (0, 0) }
            return value
        }
        return Reading(busy: busy, worstStall: worst, lateFrames: late)
    }

    /// Starts timing one action.
    public func beginEpisode() {
        episode.withLock { $0 = 0 }
    }

    /// The longest stall since `beginEpisode()`, in milliseconds.
    public func endEpisode() -> Double {
        episode.withLock { $0 }
    }

    /// Made outside the main actor: in Swift 6, a closure made inside `start()` would inherit its isolation and trap when the timer fires on `queue`.
    private nonisolated func makePinger() -> DispatchSourceTimer {
        let timer = DispatchSource.makeTimerSource(queue: queue)
        timer.schedule(deadline: .now(), repeating: .milliseconds(8))
        timer.setEventHandler { @Sendable [weak self] in
            let posted = Self.now()
            DispatchQueue.main.async { @Sendable in self?.record(waited: (Self.now() - posted) * 1000) }
        }
        timer.resume()
        return timer
    }

    private func record(waited: Double) {
        stalls.withLock { value in
            value.worst = max(value.worst, waited)
            if waited > 16.7 { value.late += 1 }
        }
        episode.withLock { $0 = max($0, waited) }
    }

    private func cpuTime() -> Double {
        var info = thread_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<thread_basic_info_data_t>.size / MemoryLayout<integer_t>.size)
        let result = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
                thread_info(mainThread, thread_flavor_t(THREAD_BASIC_INFO), $0, &count)
            }
        }
        guard result == KERN_SUCCESS else { return 0 }
        let user = Double(info.user_time.seconds) + Double(info.user_time.microseconds) / 1e6
        let system = Double(info.system_time.seconds) + Double(info.system_time.microseconds) / 1e6
        return user + system
    }

    private static func now() -> Double {
        Double(DispatchTime.now().uptimeNanoseconds) / 1e9
    }
}
