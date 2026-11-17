#!/usr/bin/env python3
"""
generate_all_presentations.py
Generates professional widescreen Microsoft PowerPoint (.pptx) presentations
and Marp Markdown slides for both research projects:
1. ComAgent: Reliability-Aware Wireless Resource Allocation (28 Slides)
2. SUPPLYCHAIN-X: AI-Driven Blockchain Framework for Supply Chain Traceability (15 Slides)

Built using pure Python standard libraries (zipfile, xml.etree.ElementTree).
No external dependencies required!
"""

import os
import sys
import zipfile
import html

def escape_xml(s: str) -> str:
    """Escapes string for inclusion in XML text nodes."""
    return html.escape(str(s), quote=True)

def build_pptx(filename: str, deck_title: str, subtitle: str, slides_data: list, accent_color: str = "38BDF8"):
    """
    Constructs a standards-compliant ECMA-376 OpenXML PPTX file.
    """
    total = len(slides_data)
    
    # [Content_Types].xml
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    content_types.append('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">')
    content_types.append('  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>')
    content_types.append('  <Default Extension="xml" ContentType="application/xml"/>')
    content_types.append('  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>')
    content_types.append('  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>')
    content_types.append('  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>')
    content_types.append('  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>')
    for i in range(1, total + 1):
        content_types.append(f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    content_types.append('</Types>')
    content_types_xml = '\n'.join(content_types)

    # _rels/.rels
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

    # ppt/_rels/presentation.xml.rels
    pres_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    pres_rels.append('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">')
    pres_rels.append('  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>')
    for i in range(1, total + 1):
        pres_rels.append(f'  <Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
    pres_rels.append('</Relationships>')
    pres_rels_xml = '\n'.join(pres_rels)

    # ppt/presentation.xml
    pres = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    pres.append('<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">')
    pres.append('  <p:sldMasterIdLst>')
    pres.append('    <p:sldMasterId id="2147483648" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>')
    pres.append('  </p:sldMasterIdLst>')
    pres.append('  <p:sldIdLst>')
    for i in range(1, total + 1):
        pres.append(f'    <p:sldId id="{255 + i}" r:id="rId{i+1}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>')
    pres.append('  </p:sldIdLst>')
    # Widescreen 16:9 dimensions: 9144000 x 5143500 EMUs (10in x 5.625in)
    pres.append('  <p:sldSz cx="9144000" cy="5143500"/>')
    pres.append('  <p:notesSz cx="6858000" cy="9144000"/>')
    pres.append('</p:presentation>')
    pres_xml = '\n'.join(pres)

    # ppt/theme/theme1.xml
    theme_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="ComAgent Slate Theme">
  <a:themeElements>
    <a:clrScheme name="SlateDark">
      <a:dk1><a:srgbClr val="0F172A"/></a:dk1>
      <a:lt1><a:srgbClr val="F8FAFC"/></a:lt1>
      <a:dk2><a:srgbClr val="1E293B"/></a:dk2>
      <a:lt2><a:srgbClr val="F1F5F9"/></a:lt2>
      <a:accent1><a:srgbClr val="{accent_color}"/></a:accent1>
      <a:accent2><a:srgbClr val="6366F1"/></a:accent2>
      <a:accent3><a:srgbClr val="10B981"/></a:accent3>
      <a:accent4><a:srgbClr val="F59E0B"/></a:accent4>
      <a:accent5><a:srgbClr val="EC4899"/></a:accent5>
      <a:accent6><a:srgbClr val="8B5CF6"/></a:accent6>
      <a:hlink><a:srgbClr val="38BDF8"/></a:hlink>
      <a:folHlink><a:srgbClr val="818CF8"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Modern">
      <a:majorFont><a:latin typeface="Segoe UI"/></a:majorFont>
      <a:minorFont><a:latin typeface="Segoe UI"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>"""

    master_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""

    layout_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""

    master_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>
  </p:sldLayoutIdLst>
</p:sldMaster>"""

    layout_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""

    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types_xml)
        z.writestr('_rels/.rels', root_rels)
        z.writestr('ppt/presentation.xml', pres_xml)
        z.writestr('ppt/_rels/presentation.xml.rels', pres_rels_xml)
        z.writestr('ppt/theme/theme1.xml', theme_xml)
        z.writestr('ppt/slideMasters/slideMaster1.xml', master_xml)
        z.writestr('ppt/slideMasters/_rels/slideMaster1.xml.rels', master_rels)
        z.writestr('ppt/slideLayouts/slideLayout1.xml', layout_xml)
        z.writestr('ppt/slideLayouts/_rels/slideLayout1.xml.rels', layout_rels)

        for i, slide in enumerate(slides_data, start=1):
            slide_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""
            z.writestr(f'ppt/slides/_rels/slide{i}.xml.rels', slide_rels)

            category = escape_xml(slide.get("category", deck_title))
            title = escape_xml(slide.get("title", f"Slide {i}"))
            bullets = slide.get("bullets", [])
            speaker = escape_xml(slide.get("speaker", "Presenter"))

            # Build bullet paragraphs
            bullet_xml_parts = []
            for b in bullets:
                escaped_b = escape_xml(b)
                bullet_xml_parts.append(f"""
        <a:p>
          <a:pPr marL="288000" indent="-288000">
            <a:buFont typeface="Arial"/>
            <a:buChar char="•"/>
          </a:pPr>
          <a:r>
            <a:rPr lang="en-US" sz="1500">
              <a:solidFill><a:srgbClr val="E2E8F0"/></a:solidFill>
            </a:rPr>
            <a:t>{escaped_b}</a:t>
          </a:r>
        </a:p>""")
            bullet_body = '\n'.join(bullet_xml_parts)

            slide_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill><a:srgbClr val="0F172A"/></a:solidFill>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      
      <!-- Category Badge Top Left -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Category"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="609600" y="380000"/><a:ext cx="6000000" cy="300000"/></a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="1100" b="1">
                <a:solidFill><a:srgbClr val="{accent_color}"/></a:solidFill>
              </a:rPr>
              <a:t>{category.upper()}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

      <!-- Slide Counter Top Right -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="Counter"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="7200000" y="380000"/><a:ext cx="1334400" cy="300000"/></a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="r"/>
            <a:r>
              <a:rPr lang="en-US" sz="1100">
                <a:solidFill><a:srgbClr val="64748B"/></a:solidFill>
              </a:rPr>
              <a:t>SLIDE {i:02d} / {total:02d}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

      <!-- Slide Title -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="4" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="609600" y="700000"/><a:ext cx="7924800" cy="750000"/></a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" b="1" sz="2400">
                <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
              </a:rPr>
              <a:t>{title}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

      <!-- Main Content / Bullets Box -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="5" name="Content"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="609600" y="1500000"/><a:ext cx="7924800" cy="3000000"/></a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          {bullet_body}
        </p:txBody>
      </p:sp>

      <!-- Footer Bar -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="6" name="Footer"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="609600" y="4700000"/><a:ext cx="7924800" cy="300000"/></a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="950">
                <a:solidFill><a:srgbClr val="475569"/></a:solidFill>
              </a:rPr>
              <a:t>Department of Computer Science &amp; Engineering • Presidency University, Bengaluru • 2026</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""
            z.writestr(f'ppt/slides/slide{i}.xml', slide_xml)

    print(f"✅ Generated {filename} ({total} slides) successfully!")


# ---------------------------------------------------------------------------
# DECK 1: COMAGENT (28 SLIDES)
# ---------------------------------------------------------------------------
comagent_slides = [
    {
        "category": "Research Presentation • 2026",
        "title": "COMAGENT: Reliability-Aware Wireless Resource Allocation",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Reference-grounded architecture • model snapshot • empirical trade-offs",
            "Project Team: Vaishnavi R (20241CSE0706) | Reshma K (20241CSE0694)",
            "Project Team: M B Gayatri (20241CSE0704) | Prakruthi HR (20241CSE0703)",
            "Department of Computer Science and Engineering, Presidency University, Bengaluru",
            "Live Simulator: https://spectacular-peony-b06cf6.netlify.app"
        ]
    },
    {
        "category": "01 • Presentation Map",
        "title": "What This Presentation Explains",
        "speaker": "Vaishnavi R",
        "bullets": [
            "01 Literature: What each cited work contributes to our design",
            "02 Model: Network assumptions, constraints, and Shannon rate equation",
            "03 Architecture: End-to-end data pipeline from inputs to allocation and evaluation",
            "04 Implementation: Algorithmic mechanics of Equal, Greedy, PF, and Proposed V2",
            "05 Evidence: Results, trade-offs, 95% bootstrap intervals, and research integrity"
        ]
    },
    {
        "category": "02 • Research Summary",
        "title": "Abstract in One Slide",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Research Question: Can target-aware allocation increase the number of users meeting a required rate without hiding costs in throughput or fairness?",
            "4 User Populations: 5, 10, 20, 50 users",
            "3 Target Rates: 0.5, 1.0, 2.0 Mbps across 10 random seeds (42–51)",
            "4 Methods: Equal, Greedy, Proportional Fair, Reliability Aware V2 = 480 runs",
            "Core Finding: V2 improves reliability in 8/12 scenarios, but Jain fairness is lower than Equal in all 12."
        ]
    },
    {
        "category": "03 • Motivation",
        "title": "Why Resource Allocation Is Difficult",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Physical Constraints: Finite spectrum (10 MHz) and transmit power (1.0 W)",
            "Heterogeneity: Users experience different distances, channel gains, noise, and interference",
            "Competing Objectives: Aggregate sum-rate vs. meeting per-user target rates vs. avoiding starvation",
            "Design Implication: Sum throughput alone is misleading; multi-dimensional metrics are required."
        ]
    },
    {
        "category": "04 • Literature Review",
        "title": "No Single Complete Base Paper",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Wireless Allocation: Shams 2014; Yaacoub & Dawy 2012; Ribeiro 2012",
            "Proportional Fairness: Kelly et al. 1998; Mo & Walrand 2000",
            "Fairness Measurement: Jain et al. 1984 (Quantitative metric)",
            "Rate Abstraction: Shannon 1948; Goldsmith 2005 (Capacity modeling)",
            "Uncertainty Analysis: Efron & Tibshirani 1993; Davison & Hinkley 1997",
            "Future Agent Layer: ReAct, Toolformer, AutoGen, MetaGPT"
        ]
    },
    {
        "category": "05 • Literature Traceability",
        "title": "Reference -> Architecture -> Implementation",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Shams et al. (2014): Motivates policy comparison under shared spectrum (Scenario/Allocation layer)",
            "Yaacoub & Dawy (2012): Uplink OFDMA constraint formulation (Resource Budget model)",
            "Kelly et al. (1998): Log utility proportional fairness (PF comparator baseline)",
            "Jain et al. (1984): Fairness index formula (Metrics engine)",
            "Shannon & Goldsmith: Capacity / rate equation (Rate calculator)",
            "Efron & Tibshirani: Paired bootstrap resampling (Statistical analysis)"
        ]
    },
    {
        "category": "06 • Reference Detail",
        "title": "Wireless Allocation Surveys: Design Scope",
        "speaker": "Reshma K",
        "bullets": [
            "What ComAgent Borrows: Shared problem framing, multiple allocation policies, explicit budgets (10 MHz, 1.0 W)",
            "What It Does NOT Claim: Not a complete subcarrier-level OFDMA physical scheduler",
            "What It Does NOT Claim: Not a 3GPP 5G NR PHY layer or calibrated propagation testbed",
            "Focus: Algorithmic simulation study under controlled, reproducible conditions"
        ]
    },
    {
        "category": "07 • Reference Detail",
        "title": "Kelly et al. (1998): Proportional Fair Comparator",
        "speaker": "Reshma K",
        "bullets": [
            "Core Objective: Maximize sum log(r_i) to balance aggregate throughput and fair sharing",
            "Role in ComAgent: Evaluated as a deterministic comparator baseline across all 480 runs",
            "Audit Note: In reported simulation runs, PF outputs matched Equal across several seeds",
            "Research Honesty: Openly documented as requiring a gradient step audit before claiming distinct PF behavior"
        ]
    },
    {
        "category": "08 • Reference Detail",
        "title": "Jain et al. (1984): How Fairness Is Measured",
        "speaker": "Reshma K",
        "bullets": [
            "Jain's Fairness Index: J(r) = (sum r_i)^2 / [ N * sum(r_i^2) ]",
            "Theoretical Range: [1/N, 1.0] — closer to 1.0 indicates complete equality",
            "Usage: Evaluated on achieved user rate vectors to prevent drawing false throughput-only conclusions",
            "Empirical Finding: Reliability Aware V2 has lower Jain fairness than Equal in all 12 scenarios"
        ]
    },
    {
        "category": "09 • Reference Detail",
        "title": "Shannon & Goldsmith: Achievable Rate Abstraction",
        "speaker": "Reshma K",
        "bullets": [
            "Capacity Equation: r_i = B_i * log2( 1 + [ P_i * g_i ] / [ N_i + I_i ] )",
            "B_i: Assigned bandwidth slice from 10.0 MHz global pool",
            "P_i: Assigned transmit power slice from 1.0 W global pool",
            "g_i: Channel power gain under distance pathloss and Rayleigh fading",
            "N_i + I_i: Bandwidth-scaled thermal noise floor plus modeled cross-user interference"
        ]
    },
    {
        "category": "10 • Reference Detail",
        "title": "Efron & Tibshirani: Paired Bootstrap Resampling",
        "speaker": "Reshma K",
        "bullets": [
            "Matched Differences: For each seed k, compute delta_k = Reliability_V2(k) - Reliability_Equal(k)",
            "Resampling: Draw with replacement from the paired difference vector (size 10)",
            "Scale: 20,000 independent bootstrap iterations",
            "Interval: Extract empirical 2.5th and 97.5th percentiles for a 95% Confidence Interval",
            "Settings: 10 paired seeds • Analysis RNG seed: 20261029"
        ]
    },
    {
        "category": "11 • System Model Snapshot",
        "title": "Model Snapshot: From Users to Achieved Rates",
        "speaker": "M B Gayatri",
        "bullets": [
            "Central Base Station: 10.0 MHz spectrum and 1.0 W power budget",
            "Heterogeneous Users: N in {5, 10, 20, 50} with distinct channel gains and noise",
            "Resource Allocator: Maps scenario conditions into non-negative allocation vectors (B, P)",
            "Rate Calculator: Translates allocations into achieved rates r_i",
            "Metrics Engine: Compares r_i against target threshold R_t to determine reliability"
        ]
    },
    {
        "category": "12 • Model Formulation",
        "title": "Inputs, Decision Variables, and Constraints",
        "speaker": "M B Gayatri",
        "bullets": [
            "Inputs: User count N, target rate R_t, channel gains g_i, noise N_i, interference I_i",
            "Decision Variables: Bandwidth B_i >= 0 and Transmit Power P_i >= 0 per user",
            "Programmed Budget Checks: sum(B_i) <= 10.0 MHz and sum(P_i) <= 1.0 W",
            "Non-negativity: Finite values with tolerance-aware validation assertions",
            "Validation Status: 100% (480 / 480) evaluations strictly passed budget validation"
        ]
    },
    {
        "category": "13 • Research Architecture",
        "title": "ComAgent End-to-End Pipeline",
        "speaker": "M B Gayatri",
        "bullets": [
            "Stage 1 (Scenario): Configures N, target rate R_t, random seeds 42–51",
            "Stage 2 (Channel Model): Computes gain g_i, thermal noise N_i, and interference I_i",
            "Stage 3 (Allocation): Executes Equal, Greedy, Proportional Fair, and Proposed V2",
            "Stage 4 (Rate Engine): Shannon achievable rate calculation",
            "Stage 5 (Validator): Strict validation of physical budget limits",
            "Stage 6 (Metrics & Stats): Throughput, reliability, min rate, Jain index, and bootstrap CIs"
        ]
    },
    {
        "category": "14 • Proposed Model Snapshot",
        "title": "Reliability Aware V2: Decision Flow",
        "speaker": "M B Gayatri",
        "bullets": [
            "Step 1 (Estimate Need): Calculates exact bandwidth needed for user i to hit R_t",
            "Step 2 (Sort & Prioritize): Ranks users ascending by required resource footprint",
            "Step 3 (Feasible-First): Allocates resources sequentially while remaining budget allows",
            "Step 4 (Surplus Redistribution): Greedily allocates leftover headroom to maximize throughput",
            "Characterization: Engineering heuristic prioritizing threshold satisfaction over pure fairness"
        ]
    },
    {
        "category": "15 • Model Improvement",
        "title": "Old Baseline vs Proposed V2",
        "speaker": "M B Gayatri",
        "bullets": [
            "Old Baseline (Equal Allocation): B_i = 10/N, P_i = 1.0/N. Simple, high fairness, blind to channels",
            "Proposed V2 (Reliability Aware): Target-aware feasibility prioritization + greedy remainder",
            "Strength of V2: Significantly increases percentage of users reaching target bit rate",
            "Trade-off of V2: Lower rate fairness across the user population",
            "Paradigm Shift: Symmetric resource splitting -> Target-aware threshold optimization"
        ]
    },
    {
        "category": "16 • Experiment Design",
        "title": "Reproducible Factorial Matrix",
        "speaker": "Prakruthi HR",
        "bullets": [
            "User Populations: 5, 10, 20, 50 users (4 levels)",
            "Target Rates: 0.5, 1.0, 2.0 Mbps (3 levels)",
            "Random Seeds: 42–51 (10 matched seeds per scenario)",
            "Allocation Strategies: Equal, Greedy, PF, Proposed V2 (4 methods)",
            "Total Runs: 4 * 3 * 10 * 4 = 480 evaluations (all passed budget checks)"
        ]
    },
    {
        "category": "17 • Implementation Explained",
        "title": "How Rates and Metrics Are Derived",
        "speaker": "Prakruthi HR",
        "bullets": [
            "Rate Factors: Bandwidth expansion, allocated power, channel gain, and noise floor",
            "Throughput: Sum of all user rates (total network capacity in Mbps)",
            "Reliability: Percentage of users meeting or exceeding the target threshold (r_i >= R_t)",
            "Minimum Rate: Lowest rate received by any user (cell-edge starvation check)",
            "Jain Fairness: Mathematical measurement of rate equality among users"
        ]
    },
    {
        "category": "18 • Implementation Explained",
        "title": "How the Four Allocators Differ",
        "speaker": "Prakruthi HR",
        "bullets": [
            "Equal Allocation: Splits resources symmetrically. High fairness, weak users starved of rate",
            "Greedy Allocation: Maximizes immediate total throughput. Extreme cell-edge outage",
            "Proportional Fair: Balances aggregate rate with logarithmic marginal fairness",
            "Reliability Aware V2: Optimizes resource distribution for target compliance"
        ]
    },
    {
        "category": "19 • Implementation Explained",
        "title": "Constraints & Statistical Methodology",
        "speaker": "Prakruthi HR",
        "bullets": [
            "Budget Validation: Enforces B_i >= 0, P_i >= 0, sum B <= 10 MHz, sum P <= 1.0 W",
            "Paired Seed Control: Same random seed applied across all 4 methods to isolate policy impact",
            "Resampling Uncertainty: 20,000 paired bootstrap iterations compute empirical 95% CIs",
            "Zero Crossing: An interval crossing zero indicates statistical uncertainty with 10 seeds"
        ]
    },
    {
        "category": "20 • Results Benchmark",
        "title": "Representative Benchmark: 10 Users, 1.0 Mbps",
        "speaker": "Vaishnavi R",
        "bullets": [
            "Throughput: Equal = 24.722 Mbps vs V2 = 25.353 Mbps (+2.6% increase)",
            "Reliability: Equal = 67.000% vs V2 = 77.000% (+10.0 percentage point gain)",
            "Jain Fairness: Equal = 0.570 vs V2 = 0.274 (-0.296 drop in rate equality)",
            "Core Finding: V2 satisfies 10% more users while slightly increasing sum-rate, at the cost of fairness"
        ]
    },
    {
        "category": "21 • Scenario-Wide Results",
        "title": "Does V2 Improve Reliability in Every Scenario?",
        "speaker": "Vaishnavi R",
        "bullets": [
            "IMPROVED (8 / 12 Scenarios): Strong, consistent gains under congestion (10, 20, 50 users)",
            "UNCHANGED (1 / 12 Scenarios): At 5 users, 1.0 Mbps (+0.0 pp delta)",
            "DECREASED (3 / 12 Scenarios): Strictly at 5 users (drops by 4–6 pp)",
            "Why 5 Users Dropped: At N=5, Equal already achieves near 100% reliability with abundant spectrum",
            "Fairness Observation: V2 had lower Jain fairness in all 12 scenarios without exception"
        ]
    },
    {
        "category": "22 • Visual Result Map",
        "title": "Reliability Delta Matrix: V2 minus Equal (pp)",
        "speaker": "Reshma K",
        "bullets": [
            "5 Users: 0.5 Mbps (-6.0 pp) | 1.0 Mbps (+0.0 pp) | 2.0 Mbps (-4.0 pp) -> Equal Superior",
            "10 Users: 0.5 Mbps (+20.0 pp) | 1.0 Mbps (+10.0 pp) | 2.0 Mbps (+18.0 pp) -> V2 Superior",
            "20 Users: 0.5 Mbps (+5.0 pp) | 1.0 Mbps (+19.0 pp) | 2.0 Mbps (+22.5 pp) -> V2 Superior",
            "50 Users: 0.5 Mbps (+19.6 pp) | 1.0 Mbps (+25.8 pp) | 2.0 Mbps (+20.6 pp) -> Peak Advantage",
            "Peak Observed Gain: +25.8 percentage points at 50 users, 1.0 Mbps target rate"
        ]
    },
    {
        "category": "23 • Uncertainty Analysis",
        "title": "Paired Bootstrap 95% Confidence Intervals",
        "speaker": "Reshma K",
        "bullets": [
            "10 Users, 1.0 Mbps: Delta = +10.0 pp | 95% CI: [-8.0 pp, +23.0 pp] (Includes zero -> uncertain)",
            "20 Users, 2.0 Mbps: Delta = +22.5 pp | 95% CI: [+12.5 pp, +31.0 pp] (Excludes zero -> statistically significant)",
            "50 Users, 1.0 Mbps: Delta = +25.8 pp | 95% CI: [+15.6 pp, +34.6 pp] (Excludes zero -> highly significant)",
            "Takeaway: Significant reliability advantage in congested regimes; uncertainty at small seed count in light load"
        ]
    },
    {
        "category": "24 • Limitations & Integrity",
        "title": "What the Current Evidence Does Not Prove",
        "speaker": "Prakruthi HR",
        "bullets": [
            "Shannon Abstraction: Does not model HARQ retransmissions, Doppler shift, or channel estimation error",
            "Seed Count: 10 seeds per scenario is an exploratory sample; larger campaigns needed",
            "Heuristic Scope: V2 is an engineering greedy heuristic, not a mathematically proven global optimum",
            "PF Implementation Audit: PF outputs matched Equal in several runs; requires code audit",
            "Agent Layer: Automated LLM selector tests encountered API rate limits; current findings test deterministic heuristics"
        ]
    },
    {
        "category": "25 • Conclusion & References",
        "title": "Summary of Findings & Core References",
        "speaker": "Prakruthi HR",
        "bullets": [
            "Conclusion: V2 improves reliability in 8/12 scenarios, but lowers Jain fairness in all 12",
            "V2 is a reliability-focused engineering trade-off, not a universal replacement",
            "[1] Kelly et al. (1998) - Proportional fairness and stability",
            "[2] Jain et al. (1984) - Fairness index in shared computer systems",
            "[3] Shams et al. (2014) - OFDM/OFDMA resource allocation survey",
            "[4] Yaacoub & Dawy (2012) - Uplink OFDMA resource allocation",
            "[5] Shannon (1948) & Goldsmith (2005) - Channel capacity and wireless communications",
            "[6] Efron & Tibshirani (1993) - Bootstrap methods and resampling"
        ]
    },
    {
        "category": "26 • Implementation Mapping",
        "title": "Directly Implemented vs Literature Context",
        "speaker": "Prakruthi HR",
        "bullets": [
            "Directly Implemented: Jain fairness formula coded directly into the metrics engine",
            "Model Abstraction: Shannon achievable rate equation used for user bit rates",
            "Analysis Method: 20,000-resample paired bootstrap for confidence interval reporting",
            "Literature Motivation: Kelly PF and Shams OFDMA surveys provide comparison framing",
            "Integrity: Distinguishes simulated algorithmic modules from full physical RF systems"
        ]
    },
    {
        "category": "27 • Experiment Dataset",
        "title": "Reproducible 480-Row Experiment Matrix",
        "speaker": "Vaishnavi R",
        "bullets": [
            "All 480 runs recorded with explicit random seeds, budgets, and per-user rate allocations",
            "Interactive Deck: comagent_presentation.html includes real-time scenario explorer",
            "Live Web Simulator: https://spectacular-peony-b06cf6.netlify.app",
            "GitHub Repository: https://github.com/vaishnavir26-byte/ComAgent-Wireless-Optimization.git",
            "Thank you! We welcome questions and viva discussion."
        ]
    }
]


# ---------------------------------------------------------------------------
# DECK 2: SUPPLYCHAIN-X (15 SLIDES)
# ---------------------------------------------------------------------------
supplychain_slides = [
    {
        "category": "Research Presentation • 2026",
        "title": "SUPPLYCHAIN-X: AI-Driven Blockchain Framework",
        "speaker": "Project Team",
        "bullets": [
            "An Intelligent, Hardware-Free Framework for Supply Chain Traceability and Risk Prediction",
            "Consortium Blockchain • Multi-Party Endorsements • Off-Chain IPFS • O(log N) Merkle Proofs",
            "Embedded AI Risk Engine: Random Forest ML Model with 99.5% accuracy",
            "Live Web Platform: https://spectacular-peony-b06cf6.netlify.app",
            "Presidency University, Bengaluru • Department of Computer Science & Engineering"
        ]
    },
    {
        "category": "01 • The Problem",
        "title": "Why Traditional Supply Chains Fail",
        "speaker": "Project Team",
        "bullets": [
            "Information Silos: Centralized ERP databases are opaque and vulnerable to internal manipulation",
            "Counterfeit & Tampering: $500B+ annual global trade losses due to fake provenance certificates",
            "The Hardware Dilemma: IoT RFID sensors cost $15–$50 per unit and fail in rugged agricultural settings",
            "Reactive Compliance: Audits occur months after shipment contamination or safety breaches",
            "Our Solution: Cryptographic digital signatures + off-chain IPFS + proactive AI risk prediction"
        ]
    },
    {
        "category": "02 • Objectives",
        "title": "Objectives & Hardware-Free Scope",
        "speaker": "Project Team",
        "bullets": [
            "Hardware-Free Traceability: Replace expensive physical sensors with cryptographic certificates and custody handovers",
            "Immutability & Non-Repudiation: Immutable ledger with ECDSA SECP256k1 keypairs per organization",
            "Dual-Storage Architecture: On-chain SHA-256 hashes + off-chain IPFS payload storage",
            "Cryptographic Verification: O(log N) Merkle audit proofs for batch certificates",
            "Proactive Risk Prevention: Pre-shipment AI risk scoring flagging high-risk consignments before dispatch"
        ]
    },
    {
        "category": "03 • Governance",
        "title": "Consortium Roles & Digital Identity",
        "speaker": "Project Team",
        "bullets": [
            "FarmerOrgMSP: Registers agricultural harvest batches and environmental metadata",
            "ProcessorOrgMSP: Logs quality inspection, processing steps, and lab certificates",
            "DistributorOrgMSP: Manages warehouse dispatch, temperature thresholds, and custody handover",
            "RetailerOrgMSP: Confirms delivery reception, inventory placement, and shelf verification",
            "RegulatorOrgMSP: Independent oversight, automated compliance auditing, and emergency quarantine"
        ]
    },
    {
        "category": "04 • Architecture",
        "title": "Full-Stack 5-Layer Architecture",
        "speaker": "Project Team",
        "bullets": [
            "Layer 1 (Presentation): 7 Responsive Web Dashboard Screens (Tailwind CSS, Lucide)",
            "Layer 2 (API & Middleware): Threaded HTTP REST Server (FastAPI / stdlib compatible)",
            "Layer 3 (Smart Contract Engine): 13 Business Logic Methods with Role-Based Access Control",
            "Layer 4 (Consensus & Cryptography): 3-Node Raft Cluster (CFT) + Merkle Trees + SHA-256 hashing",
            "Layer 5 (Persistence & AI): SQLite relational store + Simulated IPFS + Scikit-Learn Random Forest"
        ]
    },
    {
        "category": "05 • Smart Contracts",
        "title": "13 Smart Contract Methods",
        "speaker": "Project Team",
        "bullets": [
            "Batch Creation: RegisterBatch, AddBatchCertification",
            "Supply Chain Custody: TransferCustody, UpdateBatchLocation",
            "Audit & Verification: SubmitMerkleRoot, VerifyMerkleProof",
            "AI & Risk Governance: ReportRisk, FlagInspectionRequired",
            "Compliance Enforcement: QuarantineBatch, ReleaseQuarantine, VerifyProvenance",
            "Consensus Operations: ProposeBlock, EndorseProposal (2-of-3 quorum requirement)"
        ]
    },
    {
        "category": "06 • Chain of Custody",
        "title": "6-Stage Cryptographic Chain of Custody",
        "speaker": "Project Team",
        "bullets": [
            "Stage 1 (Harvest): Farmer registers batch with geographic origin and moisture content",
            "Stage 2 (Processing): Processor verifies grain grade and issues lab certification",
            "Stage 3 (Transit): Distributor initiates freight transport and logs waybill hash",
            "Stage 4 (Distribution): Regional hub confirms temperature compliance and onward routing",
            "Stage 5 (Retail): Retailer receives shipment and completes final quality audit",
            "Stage 6 (Consumer): Consumer scans QR code to inspect complete provenance audit trail"
        ]
    },
    {
        "category": "07 • Endorsement Policy",
        "title": "Multi-Party Endorsement Policy (2-of-3 Quorum)",
        "speaker": "Project Team",
        "bullets": [
            "Zero Single Point of Trust: No single organization can unilaterally alter supply chain state",
            "Quorum Rule: High-impact actions require endorsement from at least 2 out of 3 consortium peers",
            "Cryptographic Verification: Every endorsement carries the peer's digital signature and timestamp",
            "Byzantine Rejection: If an endorsement fails signature validation, the transaction is rejected",
            "Audit Trail: Complete endorsement signatures recorded permanently in block headers"
        ]
    },
    {
        "category": "08 • Off-Chain Storage",
        "title": "IPFS Storage & O(log N) Merkle Proofs",
        "speaker": "Project Team",
        "bullets": [
            "The Blockchain Bloat Problem: Storing PDFs and lab images directly on-chain degrades performance",
            "Our Hybrid Solution: Raw files stored on IPFS; only immutable content hashes (CIDs) committed to ledger",
            "Merkle Audit Proofs: 100 shipping waybills combined into a single 32-byte Merkle root",
            "Logarithmic Efficiency: Verifying an individual document requires only O(log N) sibling hashes",
            "Storage Savings: 98% reduction in on-chain block size compared to storing full certificates"
        ]
    },
    {
        "category": "09 • Consensus Layer",
        "title": "3-Node Raft Consensus (CFT)",
        "speaker": "Project Team",
        "bullets": [
            "Consensus Choice: Crash Fault Tolerant (CFT) Raft consensus for enterprise permissioned networks",
            "3-Node Cluster: Node-1 (Leader), Node-2 (Follower), Node-3 (Follower)",
            "High Throughput: Sub-second block finality without wasteful Proof-of-Work energy consumption",
            "Resilience: Cluster tolerates failure of any single node while maintaining full write availability",
            "Automated Leader Election: Heartbeat timeout triggers election if leader disconnects"
        ]
    },
    {
        "category": "10 • AI Risk Engine",
        "title": "AI-Based Supply Chain Risk Scoring",
        "speaker": "Project Team",
        "bullets": [
            "Model Architecture: Random Forest Classifier trained on 2,500 historical shipments",
            "Model Performance: 99.5% Test Accuracy • 99.4% Precision • 99.6% Recall",
            "5 Input Features: Supplier reliability, historical delay, rejection rate, doc failures, tx irregularities",
            "Risk Classes: LOW (0–30), MEDIUM (31–60), HIGH (61–85), CRITICAL (86–100)",
            "Automated Action: Shipments with risk >= 65 are automatically flagged for physical inspection"
        ]
    },
    {
        "category": "11 • Dashboard Platform",
        "title": "7 Interactive Web Dashboard Screens",
        "speaker": "Project Team",
        "bullets": [
            "Screen 1 (Overview): Executive KPI metrics, active node health, and recent blockchain blocks",
            "Screen 2 (Batch Registration): Cryptographic batch onboarding with metadata capture",
            "Screen 3 (Chain of Custody): Interactive timeline tracking custody handovers across MSPs",
            "Screen 4 (AI Risk Engine): Real-time risk predictor with feature sliders and automated blockchain alerts",
            "Screen 5 (Consensus Monitor): Live Raft cluster status, node toggle simulator, and election logs",
            "Screen 6 (Merkle Explorer): Visual Merkle tree generator with interactive proof verification",
            "Screen 7 (Ledger Explorer): Raw block inspection with cryptographic hash validation"
        ]
    },
    {
        "category": "12 • Quality Assurance",
        "title": "Automated Test Suite (100% Pass)",
        "speaker": "Project Team",
        "bullets": [
            "Crypto & Identity: SECP256k1 key generation, digital signatures, MSP authorization checks",
            "Merkle Engine: Merkle root derivation, leaf membership proofs, invalid proof rejection",
            "Smart Contracts: 13 chaincode methods tested for RBAC rules and unauthorized access blocks",
            "Raft Consensus: Cluster elections, node failure simulation, block replication integrity",
            "AI Engine: Prediction accuracy verification, risk classification boundaries, automated flagging",
            "Pass Rate: 100% automated test pass rate across all modular unit tests"
        ]
    },
    {
        "category": "13 • Production Roadmap",
        "title": "Hyperledger Fabric Production Roadmap",
        "speaker": "Project Team",
        "bullets": [
            "Phase 1 (Completed): Full-stack functional architecture with custom Raft, Merkle, and AI engines",
            "Phase 2 (Fabric Migration): Port smart contracts to Go/Java Chaincode on Hyperledger Fabric v2.5",
            "Phase 3 (Enterprise Storage): Connect production IPFS cluster with file pinning services",
            "Phase 4 (Zero-Knowledge Proofs): Integrate zk-SNARKs for private enterprise pricing and volumes",
            "Phase 5 (Mobile App): React Native consumer verification app with instant QR scanning"
        ]
    },
    {
        "category": "14 • Conclusion",
        "title": "Conclusion & Project Summary",
        "speaker": "Project Team",
        "bullets": [
            "Delivered: A complete, hardware-free, AI-powered blockchain traceability framework",
            "Innovation: Combines immutable custody logging with proactive pre-shipment AI risk evaluation",
            "Efficiency: O(log N) Merkle verification with 98% on-chain storage savings via IPFS",
            "Performance: 99.5% AI accuracy, sub-second Raft consensus, and 100% test pass rate",
            "Impact: Eliminates expensive IoT hardware while providing indisputable audit trails for enterprise trade"
        ]
    }
]


def main():
    print("🚀 Generating Presentations for both Research Projects...")
    
    # 1. Generate ComAgent PowerPoint (.pptx)
    build_pptx(
        filename="ComAgent_Research_Presentation.pptx",
        deck_title="COMAGENT WIRELESS OPTIMIZATION",
        subtitle="Reliability-Aware Wireless Resource Allocation",
        slides_data=comagent_slides,
        accent_color="38BDF8"  # Cyan/Sky-blue
    )

    # 2. Generate SupplyChain-X PowerPoint (.pptx)
    build_pptx(
        filename="SupplyChain_X_Presentation.pptx",
        deck_title="SUPPLYCHAIN-X BLOCKCHAIN PLATFORM",
        subtitle="AI-Driven Blockchain Supply Chain Traceability",
        slides_data=supplychain_slides,
        accent_color="10B981"  # Emerald
    )

    print("\n🎉 Both PowerPoint (.pptx) presentations generated successfully!")

if __name__ == "__main__":
    main()
