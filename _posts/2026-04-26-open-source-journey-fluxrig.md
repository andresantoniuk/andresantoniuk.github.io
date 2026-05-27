---
title: "The 25-Year Long Game: From 486CORE Kernel Drivers to fluxrig"
date: 2026-04-26
author: andresantoniuk
lang: en
categories: ["technology", "opensource"]
tags: ["opensource", "fluxrig", "embedded", "history", "career"]
excerpt: "A reflection on a 25-year journey through open source, starting with kernel drivers for the world's smallest embedded PC in 1999, and culminating in the public release of fluxrig."
toc: true
comments: true
---

It’s been quite a ride. 

Yesterday, I finally hit "public" on the **fluxrig** repository. While it feels like a new beginning, this release is actually the culmination of a journey that started exactly 27 years ago, in a very different technical landscape.

### 1999: The 486CORE Spark

In July 1999, CompuLab introduced what was then the [world's smallest embedded PC](https://www.compulab.com/1999/07/22/compulab-introduces-the-worlds-smallest-embedded-pc/): the **486CORE**. It was a marvel of miniaturization for its time, and I found myself in the middle of a project that required me to go deep into the kernel.

I was writing kernel drivers for this tiny piece of hardware. Back then, "Open Source" wasn't the corporate standard it is today—it was a frontier. Dealing with the 486CORE taught me the absolute value of technical transparency. When you are writing a driver for an embedded system, you either have visibility into the logic, or you are at the mercy of a black box. 

That lesson stayed with me for the next quarter-century.

### The Consumer Decades

Since those early days, I’ve spent my career in the "trenches" of mission-critical infrastructure. From satellite telemetry systems in the early 2000s to large-scale financial transaction engines (where I became deeply involved with [jPOS](http://jpos.org/)), Open Source has been my primary toolkit.

But for a long time, I was a **passive consumer**. I used these building blocks to solve private problems for corporations. I built impressive dashboards with Elastic, resilient switches with jPOS, and complex edge orcherstrators—all behind closed doors.

I was surviving the "battle scars" of mission-critical engineering, but I wasn't sharing the medicine.

### 2026: The Producer Shift
**fluxrig** is my way of moving to the other side of the counter. It is a brand-new, **100% AI-assisted development**, built from the ground up to codify everything I’ve learned about mission-critical systems since 1999.

It is a "Protocol Patchbay" designed for the Edge. It’s what I wish I had back in the 486CORE days, and exactly what is needed for the next generation of payment system modernization.

Why now? Because the combination of 25 years of experience and the power of modern AI has allowed me to build in months what would have taken years in the past. It’s about taking those "battle scars" and turning them into a clean, modular platform.

By combining NATS, WebAssembly, and DuckDB, fluxrig provides a foundation for operational continuity that doesn't depend on a "call home" to a cloud provider. It’s open source not just as a license, but as a commitment to giving teams back their technical autonomy.

### The Full Circle

Looking back at the [1999 press release](https://www.compulab.com/1999/07/22/compulab-introduces-the-worlds-smallest-embedded-pc/) for the 486CORE, I’m reminded of how much we’ve progressed in power, but how little the core challenges have changed. We still need to move data reliably. We still need to process protocols at the edge. And we still need systems that we can trust because we can see how they work.

fluxrig is out there now. It’s no longer just a private tool; it’s a shared resource. 

Welcome to the showroom: [fluxrig.org](https://fluxrig.org/)

---
*If you have your own stories from the early embedded days or thoughts on the shift to the Sovereign Edge, I’d love to hear them in the comments.*
