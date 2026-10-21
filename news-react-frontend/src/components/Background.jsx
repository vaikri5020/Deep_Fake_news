import React from 'react';

export default function Background() {
  return (
    <div className="bg-collage" aria-hidden="true">
      <div className="bg-layer bg-layer--1" />
      <div className="bg-layer bg-layer--2" />
      <div className="bg-noise" />
      <div className="bg-overlay" />
      <div className="headline-strip s1">BREAKING NEWS • BREAKING NEWS • BREAKING NEWS • BREAKING NEWS •</div>
      <div className="headline-strip s2">WORLD TODAY • POLITICS • ECONOMY • TECHNOLOGY • SCIENCE •</div>
      <div className="headline-strip s3">FACT CHECK • VERIFIED • RELIABLE • TRUSTED SOURCE •</div>
      <div className="headline-strip s4">LATEST UPDATES • LIVE COVERAGE • EXCLUSIVE REPORT •</div>
    </div>
  );
}
