import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, StatusBar, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

const { width } = Dimensions.get('window');

export default function CCLOSMobile() {
  const [activeMode, setActiveMode] = useState('genx');
  const [aiCount, setAiCount] = useState(18);

  const modes = [
    { id: 'genx', label: 'GenX', icon: '⚡' },
    { id: 'builder', label: 'Builder', icon: '🏗️' },
    { id: 'developer', label: 'Dev', icon: '💻' },
    { id: 'crypto', label: 'Crypto', icon: '⛓️' },
    { id: 'privacy', label: 'Privacy', icon: '🔒' },
  ];

  return (
    <LinearGradient 
      colors={['#0A0E27', '#141834', '#0A0E27']} 
      style={styles.container}
    >
      <StatusBar barStyle="light-content" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.logo}>⚡ CCL OS 0.2</Text>
        <TouchableOpacity style={styles.aiStatus}>
          <Text style={styles.aiStatusText}>● {aiCount} AIs</Text>
        </TouchableOpacity>
      </View>

      {/* Mode Selector */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        style={styles.modeScroll}
        contentContainerStyle={styles.modeContainer}
      >
        {modes.map(mode => (
          <TouchableOpacity
            key={mode.id}
            style={[
              styles.modeBtn,
              activeMode === mode.id && styles.modeBtnActive
            ]}
            onPress={() => setActiveMode(mode.id)}
          >
            <Text style={styles.modeIcon}>{mode.icon}</Text>
            <Text style={[
              styles.modeLabel,
              activeMode === mode.id && styles.modeLabelActive
            ]}>{mode.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Command Bar */}
      <View style={styles.commandBar}>
        <Text style={styles.commandPlaceholder}>Type a command...</Text>
        <TouchableOpacity style={styles.executeBtn}>
          <Text style={styles.executeText}>▶</Text>
        </TouchableOpacity>
      </View>

      {/* Content Area */}
      <ScrollView style={styles.content} contentContainerStyle={styles.contentInner}>
        {activeMode === 'genx' && <GenXMode />}
        {activeMode === 'builder' && <BuilderMode />}
        {activeMode === 'developer' && <DeveloperMode />}
        {activeMode === 'crypto' && <CryptoMode />}
        {activeMode === 'privacy' && <PrivacyMode />}
      </ScrollView>
    </LinearGradient>
  );
}

function GenXMode() {
  return (
    <View style={styles.modeContent}>
      <Text style={styles.modeTitle}>⚡ GenX Mode</Text>
      <Text style={styles.modeSubtitle}>CapeChain Labs & GenX Blockchain</Text>

      <View style={styles.cardGrid}>
        <Card icon="🔗" title="Node Dashboard" badge="Online" badgeType="success" />
        <Card icon="💼" title="GenX Wallet" badge="Soon" badgeType="warning" disabled />
        <Card icon="🪙" title="Token Creator" badge="Soon" badgeType="warning" disabled />
        <Card icon="📜" title="Smart Contract Forge" badge="Soon" badgeType="warning" disabled />
        <Card icon="🎨" title="NFT Creator" badge="Soon" badgeType="warning" disabled />
        <Card icon="🚀" title="Meme Coin Launcher" badge="Soon" badgeType="warning" disabled />
      </View>
    </View>
  );
}

function BuilderMode() {
  return (
    <View style={styles.modeContent}>
      <Text style={styles.modeTitle}>🏗️ Builder Mode</Text>
      <Text style={styles.modeSubtitle}>Create apps, websites, and APIs</Text>

      <View style={styles.dreamEngine}>
        <Text style={styles.dreamTitle}>🌟 Dream-to-App Engine</Text>
        <Text style={styles.dreamDesc}>Describe your idea and watch it become reality</Text>
        <View style={styles.dreamInput}>
          <Text style={styles.dreamPlaceholder}>Build me a crypto wallet app...</Text>
        </View>
        <TouchableOpacity style={styles.dreamBtn}>
          <Text style={styles.dreamBtnText}>✨ Build My Dream</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function DeveloperMode() {
  return (
    <View style={styles.modeContent}>
      <Text style={styles.modeTitle}>💻 Developer Mode</Text>
      <Text style={styles.modeSubtitle}>Full coding environment</Text>

      <View style={styles.terminal}>
        <View style={styles.terminalHeader}>
          <Text style={styles.terminalTitle}>CCL Terminal</Text>
        </View>
        <View style={styles.terminalBody}>
          <Text style={styles.terminalLine}>CCL OS v0.2 - CapeChain Labs</Text>
          <Text style={styles.terminalLine}>Type 'help' for commands.</Text>
        </View>
      </View>
    </View>
  );
}

function CryptoMode() {
  return (
    <View style={styles.modeContent}>
      <Text style={styles.modeTitle}>⛓️ Crypto Mode</Text>
      <Text style={styles.modeSubtitle}>Web3 tools and blockchain</Text>

      <View style={styles.cardGrid}>
        <Card icon="🪙" title="Token Launchpad" badge="Soon" badgeType="warning" disabled />
        <Card icon="📜" title="Contract Library" badge="Soon" badgeType="warning" disabled />
        <Card icon="🔍" title="Explorer Widget" badge="Soon" badgeType="warning" disabled />
      </View>
    </View>
  );
}

function PrivacyMode() {
  return (
    <View style={styles.modeContent}>
      <Text style={styles.modeTitle}>🔒 Privacy Mode</Text>
      <Text style={styles.modeSubtitle}>Local AI, encrypted files</Text>

      <View style={styles.privacyBox}>
        <Text style={styles.privacyIcon}>🏠</Text>
        <Text style={styles.privacyText}>All processing happens locally. Your data never leaves the device.</Text>
      </View>
    </View>
  );
}

function Card({ icon, title, badge, badgeType, disabled }) {
  return (
    <TouchableOpacity 
      style={[styles.card, disabled && styles.cardDisabled]}
      disabled={disabled}
    >
      <Text style={styles.cardIcon}>{icon}</Text>
      <Text style={styles.cardTitle}>{title}</Text>
      {badge && (
        <View style={[styles.badge, badgeType === 'warning' ? styles.badgeWarning : styles.badgeSuccess]}>
          <Text style={styles.badgeText}>{badge}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    padding: 15,
    paddingTop: StatusBar.currentHeight + 10,
  },
  logo: { 
    fontSize: 18, 
    fontWeight: '800', 
    color: '#00D4FF',
    letterSpacing: 2,
  },
  aiStatus: {
    backgroundColor: 'rgba(0, 255, 136, 0.2)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  aiStatusText: { color: '#00FF88', fontSize: 12, fontWeight: '600' },

  modeScroll: { maxHeight: 80 },
  modeContainer: { padding: 10, gap: 8 },
  modeBtn: {
    alignItems: 'center',
    padding: 10,
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    borderRadius: 10,
    minWidth: 70,
    borderWidth: 1,
    borderColor: '#2A2F4A',
  },
  modeBtnActive: {
    backgroundColor: '#00D4FF20',
    borderColor: '#00D4FF',
  },
  modeIcon: { fontSize: 20, marginBottom: 5 },
  modeLabel: { color: '#8888AA', fontSize: 11 },
  modeLabelActive: { color: '#00D4FF', fontWeight: '700' },

  commandBar: {
    flexDirection: 'row',
    margin: 15,
    backgroundColor: 'rgba(26, 31, 58, 0.9)',
    borderRadius: 10,
    padding: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#2A2F4A',
  },
  commandPlaceholder: { flex: 1, color: '#8888AA', fontSize: 14 },
  executeBtn: {
    backgroundColor: '#00D4FF',
    padding: 8,
    borderRadius: 6,
  },
  executeText: { color: 'white', fontWeight: '700' },

  content: { flex: 1 },
  contentInner: { padding: 15 },
  modeContent: { flex: 1 },
  modeTitle: { 
    fontSize: 28, 
    fontWeight: '800', 
    color: '#00D4FF',
    marginBottom: 5,
    textShadowColor: '#00D4FF40',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  modeSubtitle: { color: '#8888AA', fontSize: 14, marginBottom: 20 },

  cardGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  card: {
    width: (width - 40) / 2,
    backgroundColor: 'rgba(26, 31, 58, 0.9)',
    borderRadius: 15,
    padding: 15,
    borderWidth: 1,
    borderColor: '#2A2F4A',
    alignItems: 'center',
  },
  cardDisabled: { opacity: 0.5 },
  cardIcon: { fontSize: 30, marginBottom: 10 },
  cardTitle: { color: 'white', fontSize: 14, fontWeight: '600', textAlign: 'center' },
  badge: { 
    position: 'absolute', 
    top: 10, 
    right: 10, 
    paddingHorizontal: 8, 
    paddingVertical: 3, 
    borderRadius: 8 
  },
  badgeWarning: { backgroundColor: 'rgba(255, 215, 0, 0.2)' },
  badgeSuccess: { backgroundColor: 'rgba(0, 255, 136, 0.2)' },
  badgeText: { fontSize: 10, fontWeight: '600', color: '#FFD700' },

  dreamEngine: {
    backgroundColor: 'rgba(26, 31, 58, 0.9)',
    borderRadius: 15,
    padding: 20,
    borderWidth: 1,
    borderColor: '#2A2F4A',
  },
  dreamTitle: { fontSize: 20, color: '#7B2FFF', marginBottom: 10 },
  dreamDesc: { color: '#8888AA', fontSize: 14, marginBottom: 15 },
  dreamInput: {
    backgroundColor: 'rgba(10, 14, 39, 0.9)',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#2A2F4A',
  },
  dreamPlaceholder: { color: '#8888AA', fontSize: 14 },
  dreamBtn: {
    backgroundColor: '#7B2FFF',
    padding: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  dreamBtnText: { color: 'white', fontSize: 16, fontWeight: '700' },

  terminal: {
    backgroundColor: 'rgba(26, 31, 58, 0.9)',
    borderRadius: 15,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#2A2F4A',
  },
  terminalHeader: {
    backgroundColor: 'rgba(10, 14, 39, 0.9)',
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#2A2F4A',
  },
  terminalTitle: { color: 'white', fontSize: 14, fontWeight: '600' },
  terminalBody: { padding: 15 },
  terminalLine: { color: '#00FF88', fontSize: 13, fontFamily: 'Courier New', marginBottom: 5 },

  privacyBox: {
    alignItems: 'center',
    padding: 30,
    backgroundColor: 'rgba(0, 212, 255, 0.05)',
    borderRadius: 15,
    borderWidth: 1,
    borderColor: '#00D4FF30',
  },
  privacyIcon: { fontSize: 50, marginBottom: 15 },
  privacyText: { color: '#8888AA', fontSize: 14, textAlign: 'center', lineHeight: 22 },
});
