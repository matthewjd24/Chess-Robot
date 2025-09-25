CXX ?= g++
TARGET ?= program
SRCS := $(wildcard *.cpp)
OBJS := $(SRCS:.cpp=.o)

PKG_CONFIG ?= pkg-config
HAVE_PAHO := $(shell $(PKG_CONFIG) --exists paho-mqttpp3 && echo yes || echo no)

ifeq ($(HAVE_PAHO),yes)
  MQTT_CFLAGS := $(shell $(PKG_CONFIG) --cflags paho-mqttpp3)
  MQTT_LIBS   := $(shell $(PKG_CONFIG) --libs   paho-mqttpp3)
else
  MQTT_CFLAGS :=
  MQTT_LIBS   := -lpaho-mqttpp3 -lpaho-mqtt3a
endif

# Compile/Link flags
CXXSTD    ?= -std=c++17
CXXWARN   ?= -Wall -Wextra -Wpedantic
CXXOPT    ?= -O2
THREADING ?= -pthread

CXXFLAGS += $(CXXSTD) $(CXXWARN) $(CXXOPT) $(MQTT_CFLAGS) $(THREADING)
LDFLAGS  +=
LDLIBS   += $(MQTT_LIBS) $(THREADING)

# Verbosity control
ifeq ($(VERBOSE),1)
Q :=
else
Q := @
endif

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	@echo [LINK] $@
	$(Q)$(CXX) $(CXXFLAGS) $(OBJS) -o $@ $(LDFLAGS) $(LDLIBS)

%.o: %.cpp
	@echo [CXX]  $<
	$(Q)$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	@echo [CLEAN]
	$(Q)rm -f $(OBJS) $(TARGET)
