import React, { useState, useEffect, useRef } from 'react';
import { 
  View, Text, StyleSheet, TouchableOpacity, ScrollView, 
  StatusBar, Dimensions, Animated, Alert 
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import * as SecureStore from 'expo-secure-store';
import { BlurView } from 'expo-blur';

const { width, height } = Dimensions.get('window');

export default function GenXMobile() {
  const [balance, setBalance] = useState(0);
  const [tapCount, setTapCount] = useState(0);
  const [energy, setEnergy] = useState(100);
  const [lastClaim, setLastClaim] = useState<number | null>(null);
  const [isPremium, setIsPremium] = useState(false);
  const [streak, setStreak] = useState(0);
  const [activeTab, setActiveTab] = useState('mine');
  
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    loadUserData();
    startPulseAnimation();
  }, []);

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.05,
          duration: 2000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const loadUserData = async () => {
    try {
      const savedBalance = await SecureStore.getItemAsync('genx_balance');
      const savedTapCount = await SecureStore.getItemAsync('genx_taps');
      const savedLastClaim = await SecureStore.getItemAsync('genx_last_claim');
      const savedPremium = await SecureStore.getItemAsync('genx_premium');
      const savedStreak = await SecureStore.getItemAsync('genx_streak');
      
      if (savedBalance) setBalance(parseInt(savedBalance));
      if (savedTapCount) setTapCount(parseInt(savedTapCount));
      if (savedLastClaim) setLastClaim(parseInt(savedLastClaim));
      if (savedPremium) setIsPremium(savedPremium === 'true');
      if (savedStreak) setStreak(parseInt(savedStreak));
    } catch (error) {
      console.log('Error loading user data:', error);
    }
  };

  const handleTap = () => {
    if (energy <= 0) {
      Alert.alert('Energy Depleted!', 'Come back in 24 hours or watch an ad to refill.');
      return;
    }

    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    const reward = isPremium ? 1.0 : 0.5;
    const newBalance = balance + reward;
    const newTapCount = tapCount + 1;
    const newEnergy = Math.max(0, energy - 1);

    setBalance(newBalance);
    setTapCount(newTapCount);
    setEnergy(newEnergy);

    SecureStore.setItemAsync('genx_balance', newBalance.toString());
    SecureStore.setItemAsync('genx_taps', newTapCount.toString());

    Animated.sequence([
      Animated.timing(scaleAnim, { toValue: 0.85, duration: 80, useNativeDriver: true }),
      Animated.timing(scaleAnim, { toValue: 1, duration: 120, useNativeDriver: true }),
    ]).start();

    if (newEnergy === 0) {
      setLastClaim(Date.now());
      SecureStore.setItemAsync('genx_last_claim', Date.now().toString());
    }
  };

  const claimDaily = () => {
    const now = Date.now();
    if (lastClaim && (now - lastClaim) < 24 * 60 * 60 * 1000) return;

    const bonus = isPremium ? 20 : 10;
    setBalance(balance + bonus);
    setEnergy(100);
    setTapCount(0);
    setLastClaim(now);
    setStreak(streak + 1);
    
    SecureStore.setItemAsync('genx_balance', (balance + bonus).toString());
    SecureStore.setItemAsync('genx_last_claim', now.toString());
    SecureStore.setItemAsync('genx_streak', (streak + 1).toString());

    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  };

  const energyPercent = (energy / 100) * 100;
  const timeUntilReset = lastClaim 
    ? Math.max(0, 24 * 60 * 60 * 1000 - (Date.now() - lastClaim))
    : 0;

  return (
    <LinearGradient 
      colors={['#0A0E27', '#141834', '#0A0E27']} 
      style={styles.container}
    >
      <StatusBar barStyle="light-content" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>GenX Mining</Text>
        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>BALANCE</Text>
          <Text style={styles.balance}>{balance.toFixed(1)} GENX</Text>
          <Text style={styles.usdValue}>≈ ${(balance * 0.10).toFixed(2)}</Text>
        </View>
        {streak > 0 && (
          <View style={styles.streakBadge}>
            <Text style={styles.streakText}>🔥 {streak} Day Streak</Text>
          </View>
        )}
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabBar}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'mine' && styles.tabActive]} 
          onPress={() => setActiveTab('mine')}
        >
          <Text style={[styles.tabIcon, activeTab === 'mine' && styles.tabIconActive]}>⛏️</Text>
          <Text style={[styles.tabLabel, activeTab === 'mine' && styles.tabLabelActive]}>Mine</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'wallet' && styles.tabActive]} 
          onPress={() => setActiveTab('wallet')}
        >
          <Text style={[styles.tabIcon, activeTab === 'wallet' && styles.tabIconActive]}>💼</Text>
          <Text style={[styles.tabLabel, activeTab === 'wallet' && styles.tabLabelActive]}>Wallet</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'stats' && styles.tabActive]} 
          onPress={() => setActiveTab('stats')}
        >
          <Text style={[styles.tabIcon, activeTab === 'stats' && styles.tabIconActive]}>📊</Text>
          <Text style={[styles.tabLabel, activeTab === 'stats' && styles.tabLabelActive]}>Stats</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'premium' && styles.tabActive]} 
          onPress={() => setActiveTab('premium')}
        >
          <Text style={[styles.tabIcon, activeTab === 'premium' && styles.tabIconActive]}>⭐</Text>
          <Text style={[styles.tabLabel, activeTab === 'premium' && styles.tabLabelActive]}>Premium</Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView style={styles.content} contentContainerStyle={styles.contentInner}>
        {activeTab === 'mine' && (
          <View style={styles.mineContent}>
            {/* Mining Button */}
            <TouchableOpacity 
              activeOpacity={0.9} 
              onPress={handleTap}
              disabled={energy <= 0}
            >
              <Animated.View style={[
                styles.miningButtonOuter,
                { transform: [{ scale: pulseAnim }] }
              ]}>
                <LinearGradient
                  colors={energy > 0 ? ['#00D4FF20', '#7B2FFF20'] : ['#33333320', '#55555520']}
                  style={styles.miningButtonGlow}
                >
                  <Animated.View style={[
                    styles.miningButton,
                    { transform: [{ scale: scaleAnim }] }
                  ]}>
                    <LinearGradient
                      colors={energy > 0 ? ['#00D4FF', '#7B2FFF'] : ['#444', '#666']}
                      style={styles.miningGradient}
                    >
                      <Text style={styles.coinSymbol}>G</Text>
                      <Text style={styles.tapText}>TAP TO MINE</Text>
                      <Text style={styles.rewardText}>+{isPremium ? '1.0' : '0.5'} GENX</Text>
                    </LinearGradient>
                  </Animated.View>
                </LinearGradient>
              </Animated.View>
            </TouchableOpacity>

            {/* Energy Bar */}
            <View style={styles.energyContainer}>
              <View style={styles.energyBar}>
                <View style={[styles.energyFill, { width: `${energyPercent}%` }]} />
              </View>
              <View style={styles.energyRow}>
                <Text style={styles.energyText}>⚡ {energy}/100 Energy</Text>
                {isPremium && <Text style={styles.premiumBadge}>⭐ 2x</Text>}
              </View>
            </View>

            <Text style={styles.tapCount}>Taps today: {tapCount}/100</Text>

            {/* Daily Bonus */}
            <TouchableOpacity 
              style={[styles.dailyButton, timeUntilReset > 0 && styles.dailyButtonDisabled]} 
              onPress={claimDaily}
              disabled={timeUntilReset > 0}
            >
              <LinearGradient
                colors={timeUntilReset > 0 ? ['#333', '#444'] : ['#FFD700', '#FFA500']}
                style={styles.dailyGradient}
              >
                <Text style={styles.dailyEmoji}>{timeUntilReset > 0 ? '⏰' : '🎁'}</Text>
                <Text style={styles.dailyButtonText}>
                  {timeUntilReset > 0 
                    ? `${Math.floor(timeUntilReset / (1000 * 60 * 60))}h ${Math.ceil((timeUntilReset % (1000 * 60 * 60)) / (1000 * 60))}m`
                    : `Claim Daily Bonus (+${isPremium ? '20' : '10'} GENX)`
                  }
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        )}

        {activeTab === 'wallet' && <WalletScreen />}
        {activeTab === 'stats' && <StatsScreen />}
        {activeTab === 'premium' && <PremiumScreen />}
      </ScrollView>
    </LinearGradient>
  );
}

function WalletScreen() {
  const [balance, setBalance] = useState(0);
  
  useEffect(() => {
    loadBalance();
  }, []);

  const loadBalance = async () => {
    const saved = await SecureStore.getItemAsync('genx_balance');
    if (saved) setBalance(parseInt(saved));
  };

  return (
    <View style={styles.walletContent}>
      <View style={styles.walletCard}>
        <Text style={styles.walletLabel}>GENX BALANCE</Text>
        <Text style={styles.walletBalance}>{balance.toFixed(1)} GENX</Text>
        <Text style={styles.walletUsd}>≈ ${(balance * 0.10).toFixed(2)} USD</Text>
      </View>

      <TouchableOpacity 
        style={styles.adButton}
        onPress={() => Alert.alert('Watch Ad', 'Reward: +5 GENX\n\nComing soon!')}
      >
        <Text style={styles.adButtonText}>📺 Watch Ad (+5 GENX)</Text>
      </TouchableOpacity>

      <View style={styles.buyButtons}>
        <TouchableOpacity style={styles.buyButton} onPress={() => {}}>
          <Text style={styles.buyAmount}>100 GENX</Text>
          <Text style={styles.buyPrice}>$10</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.buyButton} onPress={() => {}}>
          <Text style={styles.buyAmount}>500 GENX</Text>
          <Text style={styles.buyPrice}>$45</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.buyButton} onPress={() => {}}>
          <Text style={styles.buyAmount}>1000 GENX</Text>
          <Text style={styles.buyPrice}>$80</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function StatsScreen() {
  const [balance, setBalance] = useState(0);
  const [tapCount, setTapCount] = useState(0);
  const [streak, setStreak] = useState(0);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    const bal = await SecureStore.getItemAsync('genx_balance');
    const taps = await SecureStore.getItemAsync('genx_taps');
    const strk = await SecureStore.getItemAsync('genx_streak');
    if (bal) setBalance(parseInt(bal));
    if (taps) setTapCount(parseInt(taps));
    if (strk) setStreak(parseInt(strk));
  };

  return (
    <View style={styles.statsContent}>
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{balance.toFixed(1)}</Text>
          <Text style={styles.statLabel}>Total Mined</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{tapCount}</Text>
          <Text style={styles.statLabel}>Today's Taps</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{streak}</Text>
          <Text style={styles.statLabel}>Day Streak</Text>
        </View>
      </View>

      <View style={styles.achievement}>
        <Text style={styles.achievementIcon}>🎉</Text>
        <View style={styles.achievementContent}>
          <Text style={styles.achievementTitle}>First Tap</Text>
          <Text style={styles.achievementDesc}>Started mining journey</Text>
        </View>
      </View>
    </View>
  );
}

function PremiumScreen() {
  const [isPremium, setIsPremium] = useState(false);

  useEffect(() => {
    checkPremium();
  }, []);

  const checkPremium = async () => {
    const prem = await SecureStore.getItemAsync('genx_premium');
    if (prem === 'true') setIsPremium(true);
  };

  return (
    <View style={styles.premiumContent}>
      {isPremium && (
        <View style={styles.premiumBadgeLarge}>
          <Text style={styles.premiumBadgeText}>⭐ PREMIUM ACTIVE</Text>
        </View>
      )}

      <View style={styles.benefits}>
        <View style={styles.benefitItem}>
          <Text style={styles.benefitIcon}>🚀</Text>
          <View style={styles.benefitContent}>
            <Text style={styles.benefitTitle}>2x Mining Rewards</Text>
            <Text style={styles.benefitDesc}>Earn 1.0 GENX per tap</Text>
          </View>
        </View>
        <View style={styles.benefitItem}>
          <Text style={styles.benefitIcon}>🚫</Text>
          <View style={styles.benefitContent}>
            <Text style={styles.benefitTitle}>No Ads</Text>
            <Text style={styles.benefitDesc}>Enjoy ad-free experience</Text>
          </View>
        </View>
        <View style={styles.benefitItem}>
          <Text style={styles.benefitIcon}>⚡</Text>
          <View style={styles.benefitContent}>
            <Text style={styles.benefitTitle}>2x Daily Bonus</Text>
            <Text style={styles.benefitDesc}>Get 20 GENX daily</Text>
          </View>
        </View>
      </View>

      {!isPremium ? (
        <TouchableOpacity 
          style={styles.purchaseButton}
          onPress={() => Alert.alert('Purchase', 'Premium: $4.99/month\n\nComing soon to App Store!')}
        >
          <Text style={styles.purchaseText}>$4.99/month - Get Premium</Text>
        </TouchableOpacity>
      ) : (
        <View style={styles.currentPlan}>
          <Text style={styles.currentPlanText}>Premium Member</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: StatusBar.currentHeight || 44 },
  header: { alignItems: 'center', padding: 20, paddingBottom: 10 },
  title: { fontSize: 28, fontWeight: '800', color: '#00D4FF', letterSpacing: 2 },
  balanceCard: {
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    padding: 15,
    borderRadius: 15,
    alignItems: 'center',
    marginTop: 10,
    minWidth: width * 0.8,
    borderWidth: 1,
    borderColor: 'rgba(0, 212, 255, 0.3)',
  },
  balanceLabel: { fontSize: 11, color: '#8888AA', letterSpacing: 2, fontWeight: '600' },
  balance: { fontSize: 36, fontWeight: '800', color: '#FFFFFF', marginTop: 5 },
  usdValue: { fontSize: 14, color: '#00D4FF', marginTop: 5 },
  streakBadge: {
    backgroundColor: 'rgba(255, 107, 0, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    marginTop: 10,
  },
  streakText: { color: '#FF6B00', fontSize: 12, fontWeight: '700' },

  // Tab Bar
  tabBar: {
    flexDirection: 'row',
    backgroundColor: 'rgba(26, 31, 58, 0.9)',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: 'rgba(42, 47, 74, 0.8)',
  },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 5 },
  tabActive: { borderBottomWidth: 2, borderBottomColor: '#00D4FF' },
  tabIcon: { fontSize: 20, marginBottom: 3 },
  tabIconActive: { color: '#00D4FF' },
  tabLabel: { fontSize: 11, color: '#8888AA' },
  tabLabelActive: { color: '#00D4FF', fontWeight: '700' },

  // Content
  content: { flex: 1 },
  contentInner: { padding: 20 },
  mineContent: { alignItems: 'center' },

  // Mining Button
  miningButtonOuter: {
    width: width * 0.65,
    height: width * 0.65,
    borderRadius: width * 0.325,
    overflow: 'hidden',
    elevation: 20,
  },
  miningButtonGlow: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  miningButton: {
    width: width * 0.55,
    height: width * 0.55,
    borderRadius: width * 0.275,
    overflow: 'hidden',
  },
  miningGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  coinSymbol: { fontSize: 60, fontWeight: '900', color: '#FFFFFF' },
  tapText: { fontSize: 14, fontWeight: '800', color: '#FFFFFF', marginTop: 10, letterSpacing: 2 },
  rewardText: { fontSize: 12, color: '#FFFFFF', opacity: 0.9, marginTop: 5 },

  // Energy
  energyContainer: { width: width * 0.8, marginTop: 30 },
  energyBar: {
    height: 8,
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    borderRadius: 4,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(42, 47, 74, 0.8)',
  },
  energyFill: {
    height: '100%',
    backgroundColor: '#00D4FF',
    borderRadius: 4,
  },
  energyRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 },
  energyText: { color: '#8888AA', fontSize: 12 },
  premiumBadge: { color: '#FFD700', fontSize: 11, fontWeight: '700' },
  tapCount: { color: '#666', fontSize: 13, marginTop: 15 },

  // Daily Button
  dailyButton: { marginHorizontal: 20, borderRadius: 15, overflow: 'hidden', marginTop: 20 },
  dailyButtonDisabled: { opacity: 0.6 },
  dailyGradient: { padding: 15, flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  dailyEmoji: { fontSize: 20, marginRight: 10 },
  dailyButtonText: { color: '#000', fontSize: 16, fontWeight: '800' },

  // Wallet
  walletContent: { padding: 20 },
  walletCard: {
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    marginBottom: 20,
  },
  walletLabel: { fontSize: 12, color: '#8888AA', letterSpacing: 2 },
  walletBalance: { fontSize: 32, fontWeight: '800', color: '#00D4FF', marginVertical: 5 },
  walletUsd: { fontSize: 14, color: '#8888AA' },
  adButton: {
    backgroundColor: '#7B2FFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 20,
  },
  adButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
  buyButtons: { flexDirection: 'row', gap: 10 },
  buyButton: {
    flex: 1,
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center'
  },
  buyAmount: { color: '#00D4FF', fontSize: 14, fontWeight: '700' },
  buyPrice: { color: '#8888AA', fontSize: 12, marginTop: 5 },

  // Stats
  statsContent: { padding: 20 },
  statsGrid: { flexDirection: 'row', gap: 10, marginBottom: 20 },
  statCard: {
    flex: 1,
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center'
  },
  statValue: { fontSize: 24, fontWeight: '800', color: '#00D4FF' },
  statLabel: { fontSize: 11, color: '#8888AA', marginTop: 5 },
  achievement: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    padding: 15,
    borderRadius: 10,
  },
  achievementIcon: { fontSize: 30, marginRight: 15 },
  achievementContent: { flex: 1 },
  achievementTitle: { color: '#FFF', fontSize: 16, fontWeight: '600' },
  achievementDesc: { color: '#8888AA', fontSize: 12, marginTop: 2 },

  // Premium
  premiumContent: { padding: 20 },
  premiumBadgeLarge: {
    backgroundColor: 'rgba(255, 215, 0, 0.2)',
    alignSelf: 'flex-start',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginBottom: 20,
  },
  premiumBadgeText: { color: '#FFD700', fontSize: 14, fontWeight: '800' },
  benefits: { marginBottom: 30 },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
  },
  benefitIcon: { fontSize: 30, marginRight: 15 },
  benefitContent: { flex: 1 },
  benefitTitle: { color: '#FFF', fontSize: 16, fontWeight: '600' },
  benefitDesc: { color: '#8888AA', fontSize: 12, marginTop: 2 },
  purchaseButton: {
    backgroundColor: '#FFD700',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
  },
  purchaseText: { color: '#000', fontSize: 18, fontWeight: '800' },
  currentPlan: {
    backgroundColor: 'rgba(26, 31, 58, 0.8)',
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  currentPlanText: { color: '#FFD700', fontSize: 18, fontWeight: '700' },
});
