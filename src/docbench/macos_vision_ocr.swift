import AppKit
import Foundation
import Vision

guard CommandLine.arguments.count == 2 else {
    fputs("usage: macos_vision_ocr.swift IMAGE\n", stderr)
    exit(2)
}

let path = CommandLine.arguments[1]
guard let image = NSImage(contentsOfFile: path) else {
    fputs("unable to load image\n", stderr)
    exit(2)
}

var proposed = NSRect(origin: .zero, size: image.size)
guard let cgImage = image.cgImage(forProposedRect: &proposed, context: nil, hints: nil) else {
    fputs("unable to create CGImage\n", stderr)
    exit(2)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.usesLanguageCorrection = true

do {
    try VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([request])
} catch {
    fputs("Vision request failed\n", stderr)
    exit(2)
}

let lines = (request.results ?? []).compactMap { observation -> (String, CGRect)? in
    guard let text = observation.topCandidates(1).first?.string else { return nil }
    return (text, observation.boundingBox)
}.sorted { left, right in
    let verticalDelta = left.1.midY - right.1.midY
    if abs(verticalDelta) > 0.015 { return verticalDelta > 0 }
    return left.1.minX < right.1.minX
}

for (text, _) in lines {
    print(text)
}
